from rest_framework import serializers
from api.models.message import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'content', 'context_used', 'is_user', 'created_at')
        read_only_fields = ('id', 'created_at')
