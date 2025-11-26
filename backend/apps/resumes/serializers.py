from rest_framework import serializers
from .models import Resume, ResumeTemplate

class ResumeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeTemplate
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    template_details = ResumeTemplateSerializer(source='template', read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')
