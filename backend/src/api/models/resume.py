from django.db import models
from django.conf import settings
import uuid


class CVTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    preview_image_url = models.CharField(max_length=500, blank=True, null=True)
    default_structure = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cv_templates'

    def __str__(self):
        return self.name


class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    template = models.ForeignKey(CVTemplate, on_delete=models.SET_NULL, null=True, related_name='resumes')
    title = models.CharField(max_length=300, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    professional_summary = models.TextField(blank=True)
    contact_details = models.JSONField(default=dict, blank=True)
    layout_order = models.JSONField(default=list, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resumes'

    def __str__(self):
        return self.title or f"Resume {self.id}"


class ExperienceEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience_entries')
    job_title = models.CharField(max_length=200)
    employer = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'experience_entries'


class EducationEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education_entries')
    institution = models.CharField(max_length=300)
    degree = models.CharField(max_length=200, blank=True)
    field_of_study = models.CharField(max_length=200, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'education_entries'


class ExtraActivityEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='extra_activity_entries')
    title = models.CharField(max_length=300)
    organization = models.CharField(max_length=300, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'extra_activity_entries'


class SocialLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=100)
    url = models.URLField()
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'social_links'


class SkillEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skill_entries')
    name = models.CharField(max_length=200)
    level = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'skill_entries'


class LanguageEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='language_entries')
    language = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'language_entries'
