from django.db import models
from django.utils import timezone as django_timezone
from authentication.models import CustomUser


class SubscriptionTier(models.Model):
    """Premium subscription tiers"""
    TIER_LEVELS = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]
    
    name = models.CharField(max_length=20, choices=TIER_LEVELS, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2)
    setup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Features
    max_specialists = models.PositiveIntegerField(default=1)
    max_wellness_plans = models.PositiveIntegerField(default=1)
    concierge_support = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    ai_coaching = models.BooleanField(default=False)
    
    # Perks
    features = models.JSONField(default=list, help_text="List of tier-specific features")
    perks = models.JSONField(default=list, help_text="Additional perks and benefits")
    
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order']
    
    def __str__(self):
        return self.display_name


class UserSubscription(models.Model):
    """User subscription management"""
    SUBSCRIPTION_STATUS = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='subscription')
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.CASCADE, related_name='subscriptions')
    
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='trial')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Dates
    start_date = models.DateTimeField(default=django_timezone.now)
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(blank=True, null=True)
    next_billing_date = models.DateTimeField(blank=True, null=True)
    
    # Usage tracking
    specialists_used = models.PositiveIntegerField(default=0)
    wellness_plans_used = models.PositiveIntegerField(default=0)
    concierge_requests_used = models.PositiveIntegerField(default=0)
    
    # Payment
    stripe_subscription_id = models.CharField(max_length=200, blank=True)
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.tier.display_name}"
    
    def is_active(self):
        return self.status == 'active' and self.end_date > django_timezone.now()


class Platform(models.Model):
    """Platform-wide settings and configuration"""
    name = models.CharField(max_length=100, default='VELORA')
    tagline = models.CharField(max_length=200, default='PREMIUM WELLNESS PLATFORM')
    description = models.TextField()
    
    # Branding
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#000000')
    secondary_color = models.CharField(max_length=7, default='#ffffff')
    
    # Contact Information
    support_email = models.EmailField(default='support@velora.com')
    support_phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    
    # Social Media
    social_links = models.JSONField(default=dict, help_text="Social media links")
    
    # Platform Statistics
    total_users = models.PositiveIntegerField(default=0)
    total_specialists = models.PositiveIntegerField(default=0)
    total_wellness_plans = models.PositiveIntegerField(default=0)
    success_stories = models.PositiveIntegerField(default=0)
    
    # Settings
    maintenance_mode = models.BooleanField(default=False)
    new_user_registrations = models.BooleanField(default=True)
    trial_period_days = models.PositiveIntegerField(default=14)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Platform Settings"
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """System notifications"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('reminder', 'Reminder'),
        ('achievement', 'Achievement'),
        ('update', 'Update'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    
    # Links and Actions
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=50, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"


class UserActivity(models.Model):
    """Track user activities and engagement"""
    ACTIVITY_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('profile_update', 'Profile Update'),
        ('plan_created', 'Wellness Plan Created'),
        ('session_completed', 'Session Completed'),
        ('specialist_booked', 'Specialist Booked'),
        ('concierge_request', 'Concierge Request'),
        ('subscription_change', 'Subscription Change'),
        ('achievement_unlocked', 'Achievement Unlocked'),
        ('review_submitted', 'Review Submitted'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200)
    details = models.JSONField(default=dict, blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "User Activities"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_activity_type_display()}"


class FAQ(models.Model):
    """Frequently Asked Questions"""
    CATEGORIES = [
        ('general', 'General'),
        ('subscription', 'Subscription'),
        ('specialists', 'Specialists'),
        ('wellness_plans', 'Wellness Plans'),
        ('concierge', 'Concierge Services'),
        ('billing', 'Billing'),
        ('technical', 'Technical Support'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORIES)
    question = models.CharField(max_length=200)
    answer = models.TextField()
    
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'sort_order']
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.question}"
