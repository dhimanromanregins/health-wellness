from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'gender', 'fitness_level']
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Info', {
            'fields': ('phone_number', 'date_of_birth', 'gender', 'profile_picture', 'bio')
        }),
        ('Health Info', {
            'fields': ('height', 'weight', 'fitness_level')
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Personal Info', {
            'fields': ('email', 'phone_number', 'date_of_birth', 'gender')
        }),
    )
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'primary_goal', 'target_weight', 'activity_level', 'created_at']
    list_filter = ['primary_goal', 'activity_level']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']
