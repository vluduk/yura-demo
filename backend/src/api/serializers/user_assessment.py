from rest_framework import serializers
from api.models.user_assesment import UserAssessment


class UserAssessmentSerializer(serializers.ModelSerializer):
    llm_context = serializers.SerializerMethodField()

    class Meta:
        model = UserAssessment
        fields = (
            'id', 'user', 'answers', 'experience_level', 'experience_years', 'primary_skills',
            'work_preferences', 'suggested_path', 'service_branch', 'service_role', 'rank',
            'years_of_service', 'discharge_date', 'deployment_experience', 'leadership_experience',
            'civilian_certifications', 'disabilities_or_limits', 'security_clearance',
            'education_level', 'locality', 'benefits_awareness', 'support_needs',
            'completed', 'created_at', 'updated_at', 'llm_context'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_llm_context(self, obj):
        try:
            return obj.to_llm_context()
        except Exception:
            return ''
