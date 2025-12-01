from rest_framework import serializers
from api.models.conversation import Conversation
from .message import MessageSerializer


class ConversationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'user', 'title', 'summary_data', 'conv_type', 'created_at', 'last_active_at', 'messages')
        read_only_fields = ('id', 'created_at', 'last_active_at')
