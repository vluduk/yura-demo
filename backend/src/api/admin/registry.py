from django.contrib import admin
from api.models.conversation import Conversation
from api.models.message import Message
from api.models.business import BusinessIdea, ActionStep
from api.models.knowledge import KnowledgeCategory, KnowledgeDocument
from api.models.resume import (
    Resume, ExperienceEntry, EducationEntry, ExtraActivityEntry,
    SocialLink, SkillEntry, LanguageEntry
)
from api.models.article import Article, ArticleCategory
from api.models.user_assesment import UserAssessment


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'last_active_at')
    search_fields = ('title', 'user__email')
    readonly_fields = ('created_at', 'last_active_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'is_user', 'created_at')
    search_fields = ('content', 'conversation__id')
    readonly_fields = ('created_at',)


@admin.register(BusinessIdea)
class BusinessIdeaAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'status', 'validation_score', 'created_at')
    search_fields = ('title', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ActionStep)
class ActionStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_idea', 'title', 'status', 'step_order', 'deadline')
    search_fields = ('title', 'business_idea__title')


@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'uploader', 'category', 'created_at')
    search_fields = ('title', 'uploader__email', 'source_url')
    readonly_fields = ('created_at', 'embedding')



@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'first_name', 'last_name', 'is_primary', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExperienceEntry)
class ExperienceEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'job_title', 'employer', 'start_date', 'end_date', 'display_order')
    search_fields = ('job_title', 'employer', 'resume__title')


@admin.register(EducationEntry)
class EducationEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'institution', 'degree', 'start_date', 'end_date', 'display_order')
    search_fields = ('institution', 'degree', 'resume__title')


@admin.register(ExtraActivityEntry)
class ExtraActivityEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'title', 'organization', 'start_date', 'end_date', 'display_order')
    search_fields = ('title', 'organization', 'resume__title')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'platform', 'url', 'display_order')
    search_fields = ('platform', 'url', 'resume__title')


@admin.register(SkillEntry)
class SkillEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'name', 'level', 'display_order')
    search_fields = ('name', 'resume__title')


@admin.register(LanguageEntry)
class LanguageEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'language', 'proficiency')
    search_fields = ('language', 'resume__title')


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_published', 'is_promoted', 'views_count', 'created_at')
    search_fields = ('title', 'author__email', 'slug')
    list_filter = ('is_published', 'is_promoted')
    readonly_fields = ('created_at',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(UserAssessment)
class UserAssessmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'completed', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
