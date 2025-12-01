from django.db import models
from django.conf import settings
import uuid


class BusinessIdea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_ideas')
    title = models.CharField(max_length=500)
    status = models.CharField(max_length=50, default='BRAINSTORM')
    validation_score = models.IntegerField(default=0)
    business_canvas = models.JSONField(default=dict, blank=True)
    
    # Step-by-step validation fields
    market_analysis = models.TextField(blank=True, default='')
    financial_analysis = models.TextField(blank=True, default='')
    skills_match = models.TextField(blank=True, default='')
    risk_assessment = models.TextField(blank=True, default='')
    final_verdict = models.TextField(blank=True, default='')
    
    market_research = models.JSONField(default=dict, blank=True)
    summary_card_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_ideas'

    def __str__(self):
        return self.title


class ActionStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE, related_name='action_steps')
    title = models.CharField(max_length=300)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='PENDING')
    step_order = models.IntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'action_steps'
