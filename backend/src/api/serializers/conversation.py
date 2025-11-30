from rest_framework import serializers
from api.models.conversation import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'content', 'context_used', 'is_user', 'created_at')
        read_only_fields = ('id', 'created_at')


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'user', 'title', 'summary_data', 'created_at', 'last_active_at', 'messages')
        read_only_fields = ('id', 'created_at', 'last_active_at')
