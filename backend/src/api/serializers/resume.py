from rest_framework import serializers
from api.models.resume import (
    Resume, ExperienceEntry, EducationEntry, ExtraActivityEntry,
    SocialLink, SkillEntry, LanguageEntry
)
from django.db import transaction



class ExperienceEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceEntry
        fields = ('id', 'resume', 'job_title', 'employer', 'city', 'start_date', 'end_date', 'is_current', 'description', 'display_order')
        read_only_fields = ('id', 'resume')


class EducationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationEntry
        fields = ('id', 'resume', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'description', 'display_order')
        read_only_fields = ('id', 'resume')


class ExtraActivityEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraActivityEntry
        fields = ('id', 'resume', 'title', 'organization', 'start_date', 'end_date', 'is_current', 'description', 'display_order')
        read_only_fields = ('id', 'resume')


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ('id', 'resume', 'platform', 'url', 'display_order')
        read_only_fields = ('id', 'resume')


class SkillEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillEntry
        fields = ('id', 'resume', 'name', 'level', 'display_order')
        read_only_fields = ('id', 'resume')


class LanguageEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageEntry
        fields = ('id', 'resume', 'language', 'proficiency')
        read_only_fields = ('id', 'resume')


class ResumeSerializer(serializers.ModelSerializer):
    experience_entries = ExperienceEntrySerializer(many=True, read_only=True)
    education_entries = EducationEntrySerializer(many=True, read_only=True)
    extra_activity_entries = ExtraActivityEntrySerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    skill_entries = SkillEntrySerializer(many=True, read_only=True)
    language_entries = LanguageEntrySerializer(many=True, read_only=True)
    # Write-only fields to accept frontend data structure
    personal_info = serializers.DictField(write_only=True, required=False)
    experience = ExperienceEntrySerializer(many=True, write_only=True, required=False)
    education = EducationEntrySerializer(many=True, write_only=True, required=False)
    extra_activities = ExtraActivityEntrySerializer(many=True, write_only=True, required=False)
    languages = LanguageEntrySerializer(many=True, write_only=True, required=False)
    skills = SkillEntrySerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Resume
        fields = (
            'id', 'user', 'title', 'first_name', 'last_name', 'professional_summary',
            'contact_details', 'layout_order', 'is_primary', 'created_at', 'updated_at',
            'experience_entries', 'education_entries', 'extra_activity_entries', 'social_links',
            'skill_entries', 'language_entries',
            # Write-only fields
            'personal_info', 'experience', 'education', 'extra_activities', 'languages', 'skills'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'experience_entries', 'education_entries', 'extra_activity_entries', 'social_links', 'skill_entries', 'language_entries')
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'user': {'required': False},
        }

    def update(self, instance, validated_data):
        personal_info = validated_data.pop('personal_info', None)
        experience_data = validated_data.pop('experience', None)
        education_data = validated_data.pop('education', None)
        extra_activities_data = validated_data.pop('extra_activities', None)
        languages_data = validated_data.pop('languages', None)
        skills_data = validated_data.pop('skills', None)

        with transaction.atomic():
            # Update main fields
            if personal_info:
                instance.first_name = personal_info.get('first_name', instance.first_name)
                instance.last_name = personal_info.get('last_name', instance.last_name)
                instance.professional_summary = personal_info.get('summary', instance.professional_summary)
                
                # Update contact details
                contact_fields = ['email', 'phone', 'address', 'city', 'country']
                current_contacts = instance.contact_details or {}
                for field in contact_fields:
                    if field in personal_info:
                        current_contacts[field] = personal_info[field]
                instance.contact_details = current_contacts

            # Update other direct fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()

            # Helper to sync nested relations
            def sync_nested(model_class, related_manager, data_list):
                if data_list is None:
                    return
                
                # Delete existing
                related_manager.all().delete()
                
                # Create new
                for item in data_list:
                    # Remove id if present to force creation of new UUID
                    item.pop('id', None) 
                    model_class.objects.create(resume=instance, **item)

            # Sync nested data
            sync_nested(ExperienceEntry, instance.experience_entries, experience_data)
            sync_nested(EducationEntry, instance.education_entries, education_data)
            sync_nested(ExtraActivityEntry, instance.extra_activity_entries, extra_activities_data)
            sync_nested(LanguageEntry, instance.language_entries, languages_data)
            sync_nested(SkillEntry, instance.skill_entries, skills_data)

        return instance

    def create(self, validated_data):
        # Expecting `user` and optionally `template_id` to be provided via serializer.save(user=...)
        personal_info = validated_data.pop('personal_info', None)
        experience_data = validated_data.pop('experience', None)
        education_data = validated_data.pop('education', None)
        extra_activities_data = validated_data.pop('extra_activities', None)
        languages_data = validated_data.pop('languages', None)
        skills_data = validated_data.pop('skills', None)

        # user may be passed via serializer.save(user=...)
        user = validated_data.pop('user', None)

        with transaction.atomic():
            # Prepare base fields
            first_name = None
            last_name = None
            professional_summary = None
            contact_details = {}

            if personal_info:
                first_name = personal_info.get('first_name')
                last_name = personal_info.get('last_name')
                professional_summary = personal_info.get('summary')
                contact_fields = ['email', 'phone', 'address', 'city', 'country']
                for field in contact_fields:
                    if field in personal_info:
                        contact_details[field] = personal_info[field]

            # Build resume create kwargs
            resume_kwargs = {
                'user': user,
                'first_name': first_name or validated_data.get('first_name', ''),
                'last_name': last_name or validated_data.get('last_name', ''),
                'professional_summary': professional_summary or validated_data.get('professional_summary', ''),
                'contact_details': contact_details or validated_data.get('contact_details', {}),
                'title': validated_data.get('title', ''),
                'layout_order': validated_data.get('layout_order', []),
                'is_primary': validated_data.get('is_primary', False),
            }

            resume = Resume.objects.create(**resume_kwargs)

            # Helper to create nested relations
            def create_nested(model_class, data_list):
                if not data_list:
                    return
                for item in data_list:
                    item.pop('id', None)
                    model_class.objects.create(resume=resume, **item)

            create_nested(ExperienceEntry, experience_data)
            create_nested(EducationEntry, education_data)
            create_nested(ExtraActivityEntry, extra_activities_data)
            create_nested(LanguageEntry, languages_data)
            create_nested(SkillEntry, skills_data)

        return resume
