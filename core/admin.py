from django.contrib import admin
from .models import Platform, SubscriptionTier, UserSubscription, Notification, UserActivity, FAQ


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'tagline', 'maintenance_mode', 'new_user_registrations', 'updated_at']
    list_filter = ['maintenance_mode', 'new_user_registrations']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tagline', 'description')
        }),
        ('Branding', {
            'fields': ('logo', 'favicon', 'primary_color', 'secondary_color'),
            'classes': ['collapse']
        }),
        ('Contact', {
            'fields': ('support_email', 'support_phone', 'emergency_contact', 'social_links')
        }),
        ('Statistics', {
            'fields': ('total_users', 'total_specialists', 'total_wellness_plans', 'success_stories'),
            'classes': ['collapse']
        }),
        ('Settings', {
            'fields': ('maintenance_mode', 'new_user_registrations', 'trial_period_days')
        }),
    )


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'monthly_price', 'annual_price', 'is_active', 'sort_order']
    list_filter = ['is_active']
    ordering = ['sort_order']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'tier', 'status', 'billing_cycle', 'next_billing_date', 'auto_renew']
    list_filter = ['status', 'billing_cycle', 'tier', 'auto_renew']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'is_important', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_important']
    search_fields = ['title', 'message', 'user__email']
    raw_id_fields = ['user']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'description', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'description']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_featured', 'is_published', 'view_count', 'sort_order']
    list_filter = ['category', 'is_featured', 'is_published']
    search_fields = ['question', 'answer']
    ordering = ['category', 'sort_order']
