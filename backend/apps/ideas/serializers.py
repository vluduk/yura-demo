from rest_framework import serializers
from .models import BusinessIdea, ActionStep

class ActionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionStep
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'business_idea')

class BusinessIdeaSerializer(serializers.ModelSerializer):
    action_steps = ActionStepSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessIdea
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')
