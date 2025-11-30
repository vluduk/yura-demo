from django.db import models
import uuid


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Import Conversation lazily to avoid circular imports at module import time
    conversation = models.ForeignKey('api.Conversation', on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    context_used = models.JSONField(default=dict, blank=True)
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'

    def __str__(self):
        return f"Message {self.id} in {self.conversation_id}"
