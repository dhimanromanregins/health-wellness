from django.db import models
from django.utils import timezone as django_timezone
from authentication.models import CustomUser


class SpecialistCategory(models.Model):
    """Categories for wellness specialists"""
    CATEGORY_CHOICES = [
        ('fitness', 'Fitness & Training'),
        ('nutrition', 'Nutrition & Dietetics'),
        ('longevity', 'Longevity & Anti-aging'),
        ('mental_health', 'Mental Health & Wellness'),
        ('physiotherapy', 'Physiotherapy & Recovery'),
        ('alternative', 'Alternative Medicine'),
        ('coaching', 'Life & Performance Coaching'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Specialist Categories"
    
    def __str__(self):
        return self.display_name


class Specialist(models.Model):
    """Wellness specialists/experts"""
    TIER_CHOICES = [
        ('premium', 'Premium'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='specialist_profile')
    categories = models.ManyToManyField(SpecialistCategory, related_name='specialists')
    
    # Professional Information
    title = models.CharField(max_length=100, help_text="e.g., Dr., Prof., etc.")
    professional_summary = models.TextField()
    years_experience = models.PositiveIntegerField()
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='premium')
    
    # Credentials
    certifications = models.TextField(help_text="List of certifications and qualifications")
    education = models.TextField(help_text="Educational background")
    specializations = models.TextField(help_text="Areas of specialization")
    
    # Availability and Pricing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    consultation_rate = models.DecimalField(max_digits=10, decimal_places=2)
    available_hours = models.JSONField(default=dict, help_text="Weekly availability schedule")
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Performance Metrics
    total_clients = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_accepting_clients = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} {self.user.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.title} {self.user.get_full_name()}"


class SpecialistReview(models.Model):
    """Reviews for specialists"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    
    # Review categories
    professionalism = models.IntegerField(choices=RATING_CHOICES)
    expertise = models.IntegerField(choices=RATING_CHOICES)
    communication = models.IntegerField(choices=RATING_CHOICES)
    results = models.IntegerField(choices=RATING_CHOICES)
    
    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['specialist', 'client']
    
    def __str__(self):
        return f"Review for {self.specialist} by {self.client.get_full_name()}"


class SpecialistAvailability(models.Model):
    """Specialist availability slots"""
    WEEKDAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['specialist', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.specialist} - {self.get_day_of_week_display()}: {self.start_time}-{self.end_time}"
