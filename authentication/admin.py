from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserProfile, EmailOTP, RegistrationSession


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'email', 'username', 'first_name', 'last_name', 'membership_tier',
        'is_email_verified', 'is_staff', 'created_at'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 'gender', 'fitness_level',
        'membership_tier', 'is_email_verified', 'onboarding_completed', 'subscription_active'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Info', {
            'fields': ('phone_number', 'date_of_birth', 'gender', 'profile_picture', 'bio', 'timezone')
        }),
        ('Health Info', {
            'fields': ('height', 'weight', 'fitness_level')
        }),
        ('Platform Features', {
            'fields': ('membership_tier', 'is_email_verified', 'is_phone_verified', 
                      'onboarding_completed', 'subscription_active')
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
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
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp_code', 'purpose', 'is_verified', 'attempts', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_verified', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show only recent OTPs by default
        from django.utils import timezone
        return qs.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7))
    
    actions = ['mark_as_verified', 'delete_expired']
    
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} OTPs marked as verified.')
    mark_as_verified.short_description = "Mark selected OTPs as verified"
    
    def delete_expired(self, request, queryset):
        from django.utils import timezone
        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        self.message_user(request, f'{count} expired OTPs deleted.')
    delete_expired.short_description = "Delete expired OTPs"


@admin.register(RegistrationSession)
class RegistrationSessionAdmin(admin.ModelAdmin):
    list_display = ['email', 'session_id_short', 'status', 'created_at', 'expires_at', 'is_expired_status']
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'session_id']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'expires_at']
    ordering = ['-created_at']
    
    def session_id_short(self, obj):
        return f"{obj.session_id[:8]}..."
    session_id_short.short_description = "Session ID"
    
    def is_expired_status(self, obj):
        is_expired = obj.is_expired()
        if is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired_status.short_description = "Status"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        from django.utils import timezone
        return qs.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7))
    
    actions = ['mark_as_expired', 'cleanup_expired']
    
    def mark_as_expired(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} sessions marked as expired.')
    mark_as_expired.short_description = "Mark selected sessions as expired"
    
    def cleanup_expired(self, request, queryset):
        from django.utils import timezone
        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.update(status='expired')
        self.message_user(request, f'{count} expired sessions cleaned up.')
    cleanup_expired.short_description = "Cleanup expired sessions"
