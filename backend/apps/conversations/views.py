from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
import time

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer # Or a detailed one with messages
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'
    lookup_url_kwarg = 'conversation_id'

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Pagination for messages
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 5))
        start = (page - 1) * limit
        end = start + limit
        
        messages = instance.messages.all().order_by('-created_at')[start:end]
        # Reverse back to chronological order
        messages = reversed(messages)
        
        return Response({
            'conversation': ConversationSerializer(instance).data,
            'messages': MessageSerializer(messages, many=True).data
        })

class MessageCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        except Conversation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('request')
        file = request.FILES.get('file')

        # Save User Message
        user_msg = Message.objects.create(
            conversation=conversation,
            sender=Message.Sender.USER,
            content=content,
            file=file
        )

        # Mock AI Response Stream
        def event_stream():
            ai_msg_content = "This is a simulated AI response."
            # In reality, we would call an LLM here and stream chunks
            for char in ai_msg_content.split():
                yield f"data: {char} \n\n"
                time.sleep(0.1)
            
            # Save AI Message at the end (or start and update)
            Message.objects.create(
                conversation=conversation,
                sender=Message.Sender.AI,
                content=ai_msg_content
            )
            yield "data: [DONE]\n\n"

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

class MessageActionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, conversation_id, messages_id):
        # Regenerate
        return Response({'message': 'Regenerate not implemented in demo'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def put(self, request, conversation_id, messages_id):
        # Update
        return Response({'message': 'Update not implemented in demo'}, status=status.HTTP_501_NOT_IMPLEMENTED)
