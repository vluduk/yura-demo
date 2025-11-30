from rest_framework import serializers
from api.models.resume import (
    CVTemplate, Resume, ExperienceEntry, EducationEntry, ExtraActivityEntry,
    SocialLink, SkillEntry, LanguageEntry
)


class CVTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVTemplate
        fields = ('id', 'name', 'slug', 'preview_image_url', 'default_structure', 'is_active')
        read_only_fields = ('id',)


class ExperienceEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceEntry
        fields = ('id', 'resume', 'job_title', 'employer', 'city', 'start_date', 'end_date', 'is_current', 'description', 'display_order')
        read_only_fields = ('id',)


class EducationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationEntry
        fields = ('id', 'resume', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description', 'display_order')
        read_only_fields = ('id',)


class ExtraActivityEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraActivityEntry
        fields = ('id', 'resume', 'title', 'organization', 'start_date', 'end_date', 'is_current', 'description', 'display_order')
        read_only_fields = ('id',)


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ('id', 'resume', 'platform', 'url', 'display_order')
        read_only_fields = ('id',)


class SkillEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillEntry
        fields = ('id', 'resume', 'name', 'level', 'display_order')
        read_only_fields = ('id',)


class LanguageEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageEntry
        fields = ('id', 'resume', 'language', 'proficiency')
        read_only_fields = ('id',)


class ResumeSerializer(serializers.ModelSerializer):
    experience_entries = ExperienceEntrySerializer(many=True, read_only=True)
    education_entries = EducationEntrySerializer(many=True, read_only=True)
    extra_activity_entries = ExtraActivityEntrySerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    skill_entries = SkillEntrySerializer(many=True, read_only=True)
    language_entries = LanguageEntrySerializer(many=True, read_only=True)
    template = CVTemplateSerializer(read_only=True)

    class Meta:
        model = Resume
        fields = (
            'id', 'user', 'template', 'title', 'first_name', 'last_name', 'professional_summary',
            'contact_details', 'layout_order', 'is_primary', 'created_at', 'updated_at',
            'experience_entries', 'education_entries', 'extra_activity_entries', 'social_links',
            'skill_entries', 'language_entries'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
