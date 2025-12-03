from django.db import models
from django.conf import settings
import uuid



class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes', null=True, blank=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    professional_summary = models.TextField(blank=True, null=True)
    contact_details = models.JSONField(default=dict, blank=True, null=True)
    layout_order = models.JSONField(default=list, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resumes'

    def __str__(self):
        return self.title or f"Resume {self.id}"


class ExperienceEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience_entries', null=True, blank=True)
    job_title = models.CharField(max_length=200, blank=True, null=True)
    employer = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'experience_entries'


class EducationEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education_entries', null=True, blank=True)
    institution = models.CharField(max_length=300, blank=True, null=True)
    degree = models.CharField(max_length=200, blank=True, null=True)
    field_of_study = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'education_entries'


class ExtraActivityEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='extra_activity_entries', null=True, blank=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    organization = models.CharField(max_length=300, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'extra_activity_entries'


class SocialLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='social_links', null=True, blank=True)
    platform = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'social_links'


class SkillEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skill_entries', null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    level = models.CharField(max_length=100, blank=True, null=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'skill_entries'


class LanguageEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='language_entries', null=True, blank=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    proficiency = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'language_entries'
