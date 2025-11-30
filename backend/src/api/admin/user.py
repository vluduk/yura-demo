from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from api.models.user import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_superuser', 'is_active', 'career_selected')
    list_filter = ('role', 'is_superuser', 'is_active', 'career_selected')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar_url')}),
        ('Career', {'fields': ('career_selected',)}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    readonly_fields = ('created_at', 'last_login')
    filter_horizontal = ('groups', 'user_permissions')
