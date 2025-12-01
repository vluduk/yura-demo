from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from django.conf import settings
from django.http import StreamingHttpResponse
import os
import json

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
            pass


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

    def post(self, request, *args, **kwargs):
        user = request.user
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('content')
        if not content:
            return Response({'detail': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)

        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create new conversation with optional title and conv_type
            conv = Conversation.objects.create(
                user=user, 
                title=request.data.get('title', ''),
                conv_type=request.data.get('conv_type', '')
            )

        # Save user message
        user_msg = Message.objects.create(conversation=conv, content=content, is_user=True)

        # Prepare LLM call
        from api.services.advisor import AdvisorService
        ai_text = AdvisorService.get_ai_response(user, conv, content)

        # Save AI message (full text)
        ai_msg = Message.objects.create(conversation=conv, content=ai_text, is_user=False)

        # Update conversation last active
        conv.last_active_at = timezone.now()
        conv.save(update_fields=('last_active_at',))

        # If client requested streaming (SSE), stream character-by-character
        stream = request.GET.get('stream') or request.data.get('stream')
        if stream in (True, '1', 'true', 'True', 'yes'):
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
