from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings
from django.http import StreamingHttpResponse
from api.renderers.event_stream import EventStreamRenderer
from django.core.cache import cache
import os
import json
import logging

from api.models.conversation import Conversation, ConversationType
from api.models.message import Message
from api.models.file import UploadedFile
from api.serializers.conversation import ConversationSerializer
from api.serializers.message import MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations.
    
    Provides standard CRUD operations (list, create, retrieve, update, destroy)
    plus a custom 'chat' action for interacting with the AI assistant.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'messages__content']

    def get_queryset(self):
        """Only return conversations owned by the authenticated user."""
        queryset = Conversation.objects.filter(user=self.request.user).order_by('-last_active_at')
        
        # Filter by conversation type if provided
        conv_type = self.request.query_params.get('type')
        if conv_type:
            queryset = queryset.filter(conv_type=conv_type)
            
        return queryset

    def perform_create(self, serializer):
        """Create a conversation owned by the requesting user with optional initial AI message."""
        conv = serializer.save(user=self.request.user)
        
        # Ensure default title if not set
        if not conv.title:
            type_label = dict(ConversationType.choices).get(conv.conv_type, 'Загальна')
            conv.title = f"{type_label} - новий чат"
            conv.save(update_fields=['title'])

        # If the new conversation has no messages, ask the LLM to generate an initial assistant message
        try:
            from api.services.advisor import AdvisorService

            # Generate a starter assistant message
            initial_text = AdvisorService.generate_initial_message(self.request.user, conv)
            if initial_text:
                Message.objects.create(conversation=conv, content=initial_text, is_user=False)
        except Exception:
            # Do not block creation on LLM failures; conversation exists regardless
            logger = logging.getLogger(__name__)
            logger.exception('Failed to generate initial assistant message during conversation creation')

    def perform_destroy(self, instance):
        """Delete conversation with logging."""
        logger = logging.getLogger(__name__)
        logger.info("Deleting conversation", extra={
            "conversation_id": str(instance.id), 
            "user": getattr(self.request.user, 'email', None)
        })
        instance.delete()

    @action(detail=False, methods=['post'], renderer_classes=[EventStreamRenderer, JSONRenderer])
    def chat(self, request):
        """Accept a user message, call Google LLM, and return the AI reply."""
        user = request.user
        logger = logging.getLogger(__name__)
        
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('content')
        file_id = request.data.get('file_id')

        if not content:
            return Response({'detail': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)

        file_content = None
        if file_id:
            try:
                uploaded_file = UploadedFile.objects.get(id=file_id, user=user)
                with uploaded_file.file.open('rb') as f:
                    file_content = f.read().decode('utf-8', errors='ignore')
            except Exception as e:
                logger.warning(f"File {file_id} error: {e}")

        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            provided_title = request.data.get('title')
            conv_type = request.data.get('conv_type', '')
            type_label = dict(ConversationType.choices).get(conv_type, 'Загальна')
            default_title = f"{type_label} - новий чат"
            
            conv = Conversation.objects.create(
                user=user,
                title=provided_title or default_title,
                conv_type=conv_type
            )

        # Locking mechanism
        lock_id = f"chat_lock_{conv.id}"
        if cache.get(lock_id):
            return Response({'detail': 'Processing previous request'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        cache.set(lock_id, "true", timeout=60)

        try:
            # Regeneration logic
            regenerate = request.data.get('regenerate', False)
            if regenerate and conversation_id:
                try:
                    last_msg = conv.messages.order_by('-created_at').first()
                    if last_msg and not last_msg.is_user:
                        last_msg.delete()
                        last_msg = conv.messages.order_by('-created_at').first()
                    
                    if last_msg and last_msg.is_user:
                        # If content is provided and different, update the message
                        if content and content != last_msg.content:
                            last_msg.content = content
                            last_msg.save(update_fields=['content'])
                        
                        # Use the (potentially updated) content
                        content = last_msg.content
                    else:
                        Message.objects.create(conversation=conv, content=content, is_user=True)
                except Exception:
                    Message.objects.create(conversation=conv, content=content, is_user=True)
            else:
                Message.objects.create(conversation=conv, content=content, is_user=True)

            # Streaming check
            stream = request.GET.get('stream') or request.data.get('stream')
            is_streaming = stream in (True, '1', 'true', 'True', 'yes')
            
            from api.services.advisor import AdvisorService

            if is_streaming:
                def event_stream():
                    full_ai_text = ""
                    try:
                        ai_generator = AdvisorService.get_ai_response_stream(user, conv, content, file_content)
                        for chunk in ai_generator:
                            full_ai_text += chunk
                            payload = json.dumps({"chunk": chunk})
                            yield f"data: {payload}\n\n"
                        yield "event: done\n"
                        yield "data: {}\n\n"
                    except Exception as e:
                        logger.exception("Error during streaming")
                        payload = json.dumps({"error": str(e)})
                        yield f"data: {payload}\n\n"
                    finally:
                        cache.delete(lock_id)
                        if full_ai_text:
                            ai_msg = Message.objects.create(conversation=conv, content=full_ai_text, is_user=False)
                            conv.last_active_at = timezone.now()
                            conv.save(update_fields=('last_active_at',))
                            self._generate_title_if_needed(conv)
                
                return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

            else:
                # Non-streaming
                try:
                    ai_text = AdvisorService.get_ai_response(user, conv, content, file_content)
                except Exception as e:
                    ai_text = f"(Помилка LLM) {str(e)}"
                
                ai_msg = Message.objects.create(conversation=conv, content=ai_text, is_user=False)
                conv.last_active_at = timezone.now()
                conv.save(update_fields=('last_active_at',))
                self._generate_title_if_needed(conv)
                
                # Release lock before return
                cache.delete(lock_id)
                
                serializer = MessageSerializer(ai_msg)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            cache.delete(lock_id)
            logger.exception("Unexpected error in chat view")
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _generate_title_if_needed(self, conv):
        try:
            from api.services.advisor import AdvisorService
            msg_count = conv.messages.count()
            is_default_title = (
                not conv.title or 
                conv.title == 'Нова розмова' or 
                conv.title.endswith(' - новий чат')
            )
            if msg_count >= 2 and is_default_title:
                AdvisorService.generate_conversation_title(conv)
        except Exception:
            pass

