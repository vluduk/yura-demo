from rest_framework import serializers
from api.models.business import BusinessIdea, ActionStep


class ActionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionStep
        fields = ('id', 'business_idea', 'title', 'details', 'status', 'step_order', 'deadline', 'created_at')
        read_only_fields = ('id', 'created_at')


class BusinessIdeaSerializer(serializers.ModelSerializer):
    action_steps = ActionStepSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessIdea
        fields = (
            'id', 'user', 'title', 'status', 'validation_score', 'business_canvas',
            'market_research', 'summary_card_data', 'created_at', 'updated_at', 'action_steps'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
