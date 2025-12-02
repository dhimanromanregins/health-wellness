from django.db import models
from django.utils import timezone as django_timezone
from authentication.models import CustomUser
from specialists.models import Specialist


class WellnessPlan(models.Model):
    """AI-powered personalized wellness plans"""
    PLAN_TYPES = [
        ('comprehensive', 'Comprehensive Wellness'),
        ('fitness', 'Fitness Focus'),
        ('nutrition', 'Nutrition Focus'),
        ('mental_wellness', 'Mental Wellness'),
        ('longevity', 'Longevity & Anti-aging'),
        ('recovery', 'Recovery & Rehabilitation'),
        ('performance', 'Performance Optimization'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    PLAN_STATUS = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wellness_plans')
    specialists = models.ManyToManyField(Specialist, related_name='assigned_plans', blank=True)
    
    # Plan Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_LEVELS)
    status = models.CharField(max_length=15, choices=PLAN_STATUS, default='draft')
    
    # Duration and Schedule
    duration_weeks = models.PositiveIntegerField()
    sessions_per_week = models.PositiveIntegerField()
    estimated_time_per_session = models.PositiveIntegerField(help_text="Minutes per session")
    
    # Goals and Targets
    primary_goals = models.JSONField(default=list, help_text="List of primary goals")
    target_metrics = models.JSONField(default=dict, help_text="Target metrics and KPIs")
    success_criteria = models.TextField()
    
    # AI Configuration
    ai_model_version = models.CharField(max_length=50, default='v1.0')
    personalization_factors = models.JSONField(default=dict)
    adaptation_rules = models.JSONField(default=dict)
    
    # Progress Tracking
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    current_week = models.PositiveIntegerField(default=1)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"
    
    def get_progress_percentage(self):
        return min(100, (self.current_week / self.duration_weeks) * 100)


class PlanModule(models.Model):
    """Modules within a wellness plan"""
    MODULE_TYPES = [
        ('fitness', 'Fitness Training'),
        ('nutrition', 'Nutrition Plan'),
        ('mindfulness', 'Mindfulness & Meditation'),
        ('recovery', 'Recovery & Rest'),
        ('lifestyle', 'Lifestyle Changes'),
        ('supplementation', 'Supplementation'),
        ('monitoring', 'Health Monitoring'),
    ]
    
    plan = models.ForeignKey(WellnessPlan, on_delete=models.CASCADE, related_name='modules')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES)
    order = models.PositiveIntegerField(default=1)
    
    # Configuration
    is_mandatory = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    difficulty_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    
    # Content
    instructions = models.TextField()
    resources = models.JSONField(default=list, help_text="Links, videos, documents")
    exercises = models.JSONField(default=list, help_text="List of exercises or activities")
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.plan.title} - {self.title}"


class PlanSession(models.Model):
    """Individual sessions within a plan"""
    SESSION_STATUS = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('cancelled', 'Cancelled'),
    ]
    
    plan = models.ForeignKey(WellnessPlan, on_delete=models.CASCADE, related_name='sessions')
    module = models.ForeignKey(PlanModule, on_delete=models.CASCADE, related_name='sessions')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    week_number = models.PositiveIntegerField()
    session_number = models.PositiveIntegerField()
    status = models.CharField(max_length=15, choices=SESSION_STATUS, default='scheduled')
    
    # Scheduling
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    
    # Content
    instructions = models.TextField()
    exercises = models.JSONField(default=list)
    materials_needed = models.JSONField(default=list)
    
    # Completion tracking
    completed_at = models.DateTimeField(blank=True, null=True)
    completion_notes = models.TextField(blank=True)
    user_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], blank=True, null=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['week_number', 'session_number']
        unique_together = ['plan', 'week_number', 'session_number']
    
    def __str__(self):
        return f"{self.plan.title} - Week {self.week_number}, Session {self.session_number}"


class PlanProgress(models.Model):
    """Track user progress in wellness plans"""
    plan = models.ForeignKey(WellnessPlan, on_delete=models.CASCADE, related_name='progress_entries')
    
    date = models.DateField(default=django_timezone.now)
    week_number = models.PositiveIntegerField()
    
    # Metrics
    weight = models.FloatField(blank=True, null=True)
    body_fat_percentage = models.FloatField(blank=True, null=True)
    muscle_mass = models.FloatField(blank=True, null=True)
    
    # Performance metrics
    strength_metrics = models.JSONField(default=dict, blank=True)
    endurance_metrics = models.JSONField(default=dict, blank=True)
    flexibility_metrics = models.JSONField(default=dict, blank=True)
    
    # Wellness metrics
    energy_level = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], blank=True, null=True)
    sleep_quality = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], blank=True, null=True)
    stress_level = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], blank=True, null=True)
    mood_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True)
    achievements = models.JSONField(default=list, blank=True)
    challenges = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['plan', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.plan.title} - Progress {self.date}"
