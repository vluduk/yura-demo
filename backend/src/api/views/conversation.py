from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from django.conf import settings
import os

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


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


class ConversationChatView(APIView):
    """Accepts a user message, stores it, calls Google LLM (if configured), stores the AI reply, and returns it.

    Request JSON: { "conversation_id": <uuid, optional>, "content": "user message", "title": "optional title for new conv" }
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
            conv = Conversation.objects.create(user=user, title=request.data.get('title', ''))

        # Save user message
        user_msg = Message.objects.create(conversation=conv, content=content, is_user=True)

        # Prepare LLM call
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.environ.get('GOOGLE_API_KEY')
        ai_text = None

        if not api_key:
            # No LLM key configured: return a fallback response (echo) and a warning
            ai_text = f"(LLM not configured) Echo: {content[:1000]}"
        else:
            # Try to call Google's Generative API. This code expects `google.generativeai` to be installed.
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                # Use chat-bison or model configured in settings
                model = getattr(settings, 'GOOGLE_LLM_MODEL', 'chat-bison-001')

                # Build messages: you can extend with system prompt from settings
                system_prompt = getattr(settings, 'GOOGLE_LLM_SYSTEM_PROMPT', None)
                messages = []
                if system_prompt:
                    messages.append({'role': 'system', 'content': system_prompt})
                messages.append({'role': 'user', 'content': content})

                resp = genai.chat.create(model=model, messages=messages)

                # Extract text in common response shapes
                ai_text = None
                # genai response may have .candidates, .last, or .output
                if hasattr(resp, 'candidates') and resp.candidates:
                    ai_text = resp.candidates[0].content
                elif hasattr(resp, 'last') and resp.last:
                    ai_text = resp.last
                elif hasattr(resp, 'output') and resp.output:
                    # output may be list of dicts
                    first = resp.output[0]
                    ai_text = getattr(first, 'content', None) or first.get('content') if isinstance(first, dict) else str(first)
                else:
                    ai_text = str(resp)
            except Exception as e:
                ai_text = f"(LLM error) {str(e)}"

        # Save AI message
        ai_msg = Message.objects.create(conversation=conv, content=ai_text, is_user=False)

        # Update conversation last active
        conv.last_active_at = timezone.now()
        conv.save(update_fields=('last_active_at',))

        serializer = MessageSerializer(ai_msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
