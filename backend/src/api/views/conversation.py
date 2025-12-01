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

from api.models.conversation import Conversation
from api.models.message import Message
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


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


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
        if not content:
            logger.warning('Chat request missing content', extra={'user': getattr(user, 'email', None), 'data': request.data})
            logger.debug('Request headers: %s', dict(request.headers))
            return Response({'detail': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)

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
            default_title = 'Нова розмова'
            conv = Conversation.objects.create(
                user=user,
                title=provided_title or default_title,
                conv_type=request.data.get('conv_type', '')
            )

        # Save user message
        user_msg = Message.objects.create(conversation=conv, content=content, is_user=True)

        # Prepare LLM call
        from api.services.advisor import AdvisorService
        try:
            ai_text = AdvisorService.get_ai_response(user, conv, content)
        except Exception as e:
            logger.exception('AdvisorService.get_ai_response raised an exception')
            ai_text = f"(Помилка LLM) {str(e)}"

        logger.debug('AI response generated', extra={'ai_length': len(ai_text) if ai_text else 0})

        # Save AI message (full text)
        ai_msg = Message.objects.create(conversation=conv, content=ai_text, is_user=False)

        # Update conversation last active
        conv.last_active_at = timezone.now()
        conv.save(update_fields=('last_active_at',))

        # Try to generate a better conversation title after exchanges.
        # Use LLM-based title generation if available; otherwise fall back to a short snippet
        # of the user's message when the title is still the default.
        try:
            from api.services.advisor import AdvisorService

            # Ask AdvisorService to create/update a title (no blocking on failure)
            try:
                AdvisorService.generate_conversation_title(conv)
            except Exception:
                logger = logging.getLogger(__name__)
                logger.exception('generate_conversation_title failed')

            # If title still equals the default, set a short user-content fallback title
            if conv.title in (None, '', default_title):
                fallback = (content or '').strip()
                if fallback:
                    short = (fallback[:60] + '...') if len(fallback) > 60 else fallback
                    conv.title = short
                    conv.save(update_fields=('title',))
        except Exception:
            # Don't let title generation errors break the response flow
            logger = logging.getLogger(__name__)
            logger.exception('Unexpected error while attempting to set conversation title')

        # If client requested streaming (SSE), stream character-by-character
        stream = request.GET.get('stream') or request.data.get('stream')
        logger.debug('Stream param value', extra={'stream': stream})
        if stream in (True, '1', 'true', 'True', 'yes'):
            logger.info('Client requested streaming response', extra={'user': getattr(user, 'email', None), 'conversation_id': str(conv.id)})
            # Generator that yields SSE events for each character
            def event_stream(text: str):
                try:
                    for ch in text:
                        # JSON-encode the chunk to be safe
                        payload = json.dumps({"chunk": ch})
                        yield f"data: {payload}\n\n"
                    # signal completion
                    yield "event: done\n"
                    yield "data: {}\n\n"
                except GeneratorExit:
                    return

            return StreamingHttpResponse(event_stream(ai_text), content_type='text/event-stream')

        serializer = MessageSerializer(ai_msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
