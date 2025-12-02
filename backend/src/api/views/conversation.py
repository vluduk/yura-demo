from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from django.conf import settings
from django.http import StreamingHttpResponse
from api.renderers.event_stream import EventStreamRenderer
import os
import json
import logging

from api.models.conversation import Conversation, ConversationType
from api.models.message import Message
from api.models.file import UploadedFile
from api.serializers.conversation import ConversationSerializer
from api.serializers.message import MessageSerializer


class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-last_active_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        # Ensure the conversation is owned by the requesting user
        conv = serializer.save(user=self.request.user)

        # If the new conversation has no messages, ask the LLM to generate an initial assistant message
        try:
            from api.services.advisor import AdvisorService

            # Generate a starter assistant message
            initial_text = AdvisorService.generate_initial_message(self.request.user, conv)
            if initial_text:
                from api.models.message import Message
                Message.objects.create(conversation=conv, content=initial_text, is_user=False)
        except Exception:
            # Do not block creation on LLM failures; conversation exists regardless
            logger = logging.getLogger(__name__)
            logger.exception('Failed to generate initial assistant message during conversation creation')


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve or delete a conversation belonging to the authenticated user.

    DELETE /api/conversations/<uuid:pk> will remove the conversation and cascade-delete related messages
    because the Message model uses `on_delete=models.CASCADE` for the conversation FK.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow access to conversations owned by the requesting user
        return Conversation.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Optionally log deletion and perform any cleanup before deletion
        logger = logging.getLogger(__name__)
        logger.info("Deleting conversation", extra={"conversation_id": str(instance.id), "user": getattr(self.request.user, 'email', None)})
        instance.delete()


class ConversationChatView(APIView):
    """Accepts a user message, stores it, calls Google LLM (if configured), stores the AI reply, and returns it.

    Request JSON: { 
        "conversation_id": <uuid, optional>, 
        "content": "user message", 
        "title": "optional title for new conv",
        "conv_type": "optional conversation type"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    # Allow DRF to negotiate text/event-stream for streaming clients
    renderer_classes = (EventStreamRenderer, JSONRenderer)

    def post(self, request, *args, **kwargs):
        user = request.user
        logger = logging.getLogger(__name__)
        logger.debug('ConversationChatView POST called', extra={'user': getattr(user, 'email', None), 'path': request.path})
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('content')
        file_id = request.data.get('file_id')

        if not content:
            logger.warning('Chat request missing content', extra={'user': getattr(user, 'email', None), 'data': request.data})
            logger.debug('Request headers: %s', dict(request.headers))
            return Response({'detail': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)

        file_content = None
        if file_id:
            try:
                uploaded_file = UploadedFile.objects.get(id=file_id, user=user)
                try:
                    with uploaded_file.file.open('rb') as f:
                        raw_content = f.read()
                        file_content = raw_content.decode('utf-8', errors='ignore')
                except Exception as e:
                    logger.error(f"Error reading file {file_id}: {e}")
            except UploadedFile.DoesNotExist:
                logger.warning(f"File {file_id} not found for user")

        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                logger.warning('Conversation not found for user', extra={'user': getattr(user, 'email', None), 'conversation_id': conversation_id})
                logger.debug('Request headers: %s', dict(request.headers))
                return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create new conversation with optional title and conv_type
            # Use provided title or a sensible default for new conversations
            provided_title = request.data.get('title')
            conv_type = request.data.get('conv_type', '')
            
            # Determine default title based on type
            type_label = dict(ConversationType.choices).get(conv_type, 'Загальна')
            default_title = f"{type_label} - новий чат"
            
            conv = Conversation.objects.create(
                user=user,
                title=provided_title or default_title,
                conv_type=conv_type
            )

        # Save user message
        user_msg = Message.objects.create(conversation=conv, content=content, is_user=True)

        # Check for streaming request
        stream = request.GET.get('stream') or request.data.get('stream')
        is_streaming = stream in (True, '1', 'true', 'True', 'yes')
        
        from api.services.advisor import AdvisorService

        if is_streaming:
            logger.info('Client requested streaming response', extra={'user': getattr(user, 'email', None), 'conversation_id': str(conv.id)})
            
            def event_stream():
                full_ai_text = ""
                try:
                    # Use the new streaming method
                    ai_generator = AdvisorService.get_ai_response_stream(user, conv, content, file_content)
                    
                    for chunk in ai_generator:
                        full_ai_text += chunk
                        # Yield chunk to client
                        payload = json.dumps({"chunk": chunk})
                        yield f"data: {payload}\n\n"
                    
                    # signal completion
                    yield "event: done\n"
                    yield "data: {}\n\n"

                except Exception as e:
                    logger.exception("Error during streaming")
                    payload = json.dumps({"error": str(e)})
                    yield f"data: {payload}\n\n"
                finally:
                    # After streaming is done (or failed), save the message and process updates
                    if full_ai_text:
                        # Save AI message
                        ai_msg = Message.objects.create(conversation=conv, content=full_ai_text, is_user=False)
                        
                        # Process JSON updates
                        try:
                            from api.models.user_assesment import UserAssessment
                            assessment = UserAssessment.objects.filter(user=user).order_by('-updated_at').first()
                            if not assessment:
                                assessment = UserAssessment.objects.create(user=user)
                                
                            clean_text = AdvisorService._process_response(assessment, full_ai_text)
                            
                            # Update the message with clean text if it differs
                            if clean_text != full_ai_text:
                                ai_msg.content = clean_text
                                ai_msg.save()
                        except Exception:
                            logger.exception("Error processing post-stream updates")

                        # Update conversation last active
                        conv.last_active_at = timezone.now()
                        conv.save(update_fields=('last_active_at',))
                        
                        # Title generation logic
                        try:
                            msg_count = conv.messages.count()
                            type_label = dict(ConversationType.choices).get(conv.conv_type, 'Загальна')
                            default_title_pattern = f"{type_label} - новий чат"
                            
                            if msg_count >= 4 and (conv.title == default_title_pattern or conv.title == 'Нова розмова'):
                                AdvisorService.generate_conversation_title(conv)
                        except Exception:
                            logger.exception('Unexpected error while attempting to set conversation title')

            return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

        else:
            # Non-streaming flow
            try:
                ai_text = AdvisorService.get_ai_response(user, conv, content, file_content)
            except Exception as e:
                logger.exception('AdvisorService.get_ai_response raised an exception')
                ai_text = f"(Помилка LLM) {str(e)}"

            logger.debug('AI response generated', extra={'ai_length': len(ai_text) if ai_text else 0})

            # Save AI message (full text)
            ai_msg = Message.objects.create(conversation=conv, content=ai_text, is_user=False)

            # Update conversation last active
            conv.last_active_at = timezone.now()
            conv.save(update_fields=('last_active_at',))

            # Title generation logic
            try:
                msg_count = conv.messages.count()
                type_label = dict(ConversationType.choices).get(conv.conv_type, 'Загальна')
                default_title_pattern = f"{type_label} - новий чат"
                
                if msg_count >= 4 and (conv.title == default_title_pattern or conv.title == 'Нова розмова'):
                    AdvisorService.generate_conversation_title(conv)
            except Exception:
                logger.exception('Unexpected error while attempting to set conversation title')

            serializer = MessageSerializer(ai_msg)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
