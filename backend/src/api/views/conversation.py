from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from django.conf import settings
import os
import google.generativeai as genai

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
            # Try to call Google's Generative API (Gemini).
            try:

                genai.configure(api_key=api_key)
                model_name = getattr(settings, 'GOOGLE_LLM_MODEL', 'gemini-pro')
                
                # Handle system prompt
                system_prompt = getattr(settings, 'GOOGLE_LLM_SYSTEM_PROMPT', None)
                
                # Prepend system prompt to content
                full_prompt = content
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{content}"

                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                
                # Check if we got a valid response
                if response.parts:
                    ai_text = response.text
                else:
                    ai_text = "(No response - likely blocked by safety filters)"

            except Exception as e:
                ai_text = f"(LLM error) {str(e)}"

        # Save AI message
        ai_msg = Message.objects.create(conversation=conv, content=ai_text, is_user=False)

        # Update conversation last active
        conv.last_active_at = timezone.now()
        conv.save(update_fields=('last_active_at',))

        serializer = MessageSerializer(ai_msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
