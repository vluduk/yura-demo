from django.db import models
from django.conf import settings
import uuid

class BusinessIdea(models.Model):
    class Status(models.TextChoices):
        BRAINSTORM = 'BRAINSTORM', 'Brainstorm'
        RESEARCH = 'RESEARCH', 'Research'
        VALIDATION = 'VALIDATION', 'Validation'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ideas')
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BRAINSTORM)
    validation_score = models.IntegerField(default=0)
    
    business_canvas = models.JSONField(default=dict, blank=True)
    market_research = models.JSONField(default=dict, blank=True)
    summary_card_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ActionStep(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        DONE = 'DONE', 'Done'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name='action_steps')
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    step_order = models.IntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_order']

    def __str__(self):
        return self.title
