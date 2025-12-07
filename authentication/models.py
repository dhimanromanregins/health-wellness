from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator
import random
import string


class CustomUser(AbstractUser):
    """
    Custom user model for VELORA premium wellness platform
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    MEMBERSHIP_TIERS = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('elite', 'Elite'),
        ('concierge', 'Concierge'),
    ]
    
    # Core user information
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Premium platform features
    membership_tier = models.CharField(max_length=15, choices=MEMBERSHIP_TIERS, default='basic')
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    subscription_active = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Health related fields
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        blank=True,
        null=True
    )
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class UserProfile(models.Model):
    """
    Extended profile information for users
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Health goals
    GOAL_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('build_muscle', 'Build Muscle'),
        ('improve_endurance', 'Improve Endurance'),
        ('stress_relief', 'Stress Relief'),
        ('general_fitness', 'General Fitness'),
    ]
    
    primary_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, blank=True, null=True)
    target_weight = models.FloatField(blank=True, null=True, help_text="Target weight in kg")
    activity_level = models.CharField(
        max_length=20,
        choices=[
            ('sedentary', 'Sedentary (little/no exercise)'),
            ('lightly_active', 'Lightly Active (light exercise 1-3 days/week)'),
            ('moderately_active', 'Moderately Active (moderate exercise 3-5 days/week)'),
            ('very_active', 'Very Active (hard exercise 6-7 days/week)'),
            ('extremely_active', 'Extremely Active (very hard exercise, physical job)'),
        ],
        blank=True,
        null=True
    )
    
    # Medical information
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions or allergies")
    medications = models.TextField(blank=True, help_text="Current medications")
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Profile"


class EmailOTP(models.Model):
    """
    Model to handle email OTP verification for registration and authentication
    """
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('registration', 'Registration'),
            ('login', 'Login'),
            ('password_reset', 'Password Reset'),
            ('email_verification', 'Email Verification'),
        ],
        default='registration'
    )
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"
    
    def __str__(self):
        return f"{self.email} - {self.otp_code} ({self.purpose})"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def can_attempt(self):
        return self.attempts < self.max_attempts and not self.is_expired()
    
    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        if not self.expires_at:
            from django.conf import settings
            expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
            self.expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        super().save(*args, **kwargs)


class RegistrationSession(models.Model):
    """
    Model to track user registration sessions and progress
    """
    SESSION_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('email_sent', 'Email Sent'),
        ('email_verified', 'Email Verified'),
        ('profile_created', 'Profile Created'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    session_id = models.CharField(max_length=32, unique=True)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='initiated')
    user_data = models.JSONField(default=dict, blank=True)  # Store temporary registration data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Registration Session"
        verbose_name_plural = "Registration Sessions"
    
    def __str__(self):
        return f"{self.email} - {self.status}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @classmethod
    def generate_session_id(cls):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = self.generate_session_id()
        if not self.expires_at:
            # Registration sessions expire after 24 hours
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
