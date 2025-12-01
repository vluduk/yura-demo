from django.db import models
from django.conf import settings
import uuid


class ConversationType(models.TextChoices):
    BUSINESS = 'Business', 'Власний бізнес'
    SELF_EMPLOYMENT = 'SelfEmployment', 'Самозайнятість'
    HIRING = 'Hiring', 'Наймана праця'
    CAREER_PATH = 'CareerPath', 'Вибір напрямку'
    EDUCATION = 'Education', 'Навчання'


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=500, blank=True)
    summary_data = models.JSONField(default=dict, blank=True)
    conv_type = models.CharField(
        max_length=50, 
        choices=ConversationType.choices,
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'

    def __str__(self):
        return self.title or str(self.id)
