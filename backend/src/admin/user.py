from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from src.models.user import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = UserChangeForm
    # add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'surname', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'avatar_url', 'career_selected')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin uses it
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password', 'role'),
        }),
    )
    search_fields = ('email', 'name', 'surname')
    ordering = ('email',)
    filter_horizontal = ()
