from django.contrib import admin
from .models import BusinessIdea, ActionStep

class ActionStepInline(admin.TabularInline):
    model = ActionStep
    extra = 1

@admin.register(BusinessIdea)
class BusinessIdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'validation_score', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'user__phone')
    inlines = [ActionStepInline]

@admin.register(ActionStep)
class ActionStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'business_idea', 'status', 'deadline')
    list_filter = ('status', 'deadline')
