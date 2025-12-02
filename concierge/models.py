from django.db import models
from django.utils import timezone as django_timezone
from authentication.models import CustomUser
from specialists.models import Specialist
from wellness_plans.models import WellnessPlan


class ConciergeAgent(models.Model):
    """Dedicated concierge agents for premium support"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='concierge_profile')
    
    # Professional Information
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specializations = models.JSONField(default=list, help_text="Areas of expertise")
    languages = models.JSONField(default=list, help_text="Languages spoken")
    
    # Performance Metrics
    total_clients = models.PositiveIntegerField(default=0)
    average_response_time = models.DurationField(blank=True, null=True)
    client_satisfaction_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_requests_handled = models.PositiveIntegerField(default=0)
    
    # Availability
    is_active = models.BooleanField(default=True)
    max_concurrent_clients = models.PositiveIntegerField(default=20)
    working_hours = models.JSONField(default=dict, help_text="Weekly working schedule")
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Concierge {self.user.get_full_name()}"


class ConciergeService(models.Model):
    """Types of concierge services offered"""
    SERVICE_CATEGORIES = [
        ('scheduling', 'Appointment Scheduling'),
        ('coordination', 'Specialist Coordination'),
        ('planning', 'Wellness Plan Management'),
        ('lifestyle', 'Lifestyle Concierge'),
        ('emergency', 'Emergency Support'),
        ('consultation', 'Consultation Services'),
        ('travel', 'Wellness Travel Planning'),
        ('nutrition', 'Meal Planning & Delivery'),
        ('fitness', 'Fitness Equipment & Setup'),
        ('wellness', 'General Wellness Support'),
    ]
    
    TIER_REQUIREMENTS = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES)
    minimum_tier = models.CharField(max_length=20, choices=TIER_REQUIREMENTS, default='basic')
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_complimentary = models.BooleanField(default=False)
    
    # Service details
    estimated_completion_time = models.DurationField(blank=True, null=True)
    requires_specialist = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ConciergeRequest(models.Model):
    """Client requests for concierge services"""
    REQUEST_STATUS = [
        ('submitted', 'Submitted'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('pending_approval', 'Pending Approval'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    ]
    
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='concierge_requests')
    agent = models.ForeignKey(ConciergeAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    service = models.ForeignKey(ConciergeService, on_delete=models.CASCADE, related_name='requests')
    
    # Request Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=15, choices=PRIORITY_LEVELS, default='normal')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='submitted')
    
    # Scheduling
    preferred_date = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    estimated_completion = models.DateTimeField(blank=True, null=True)
    
    # Additional Information
    special_instructions = models.TextField(blank=True)
    budget_range = models.CharField(max_length=100, blank=True)
    location_preferences = models.TextField(blank=True)
    
    # Completion
    completed_at = models.DateTimeField(blank=True, null=True)
    completion_notes = models.TextField(blank=True)
    client_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], blank=True, null=True)
    client_feedback = models.TextField(blank=True)
    
    # Cost
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client.get_full_name()}"


class ConciergeAppointment(models.Model):
    """Appointments scheduled by concierge"""
    APPOINTMENT_TYPES = [
        ('specialist_consultation', 'Specialist Consultation'),
        ('wellness_session', 'Wellness Session'),
        ('health_screening', 'Health Screening'),
        ('fitness_assessment', 'Fitness Assessment'),
        ('nutrition_consultation', 'Nutrition Consultation'),
        ('lifestyle_planning', 'Lifestyle Planning'),
        ('follow_up', 'Follow-up Session'),
    ]
    
    APPOINTMENT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='concierge_appointments')
    agent = models.ForeignKey(ConciergeAgent, on_delete=models.CASCADE, related_name='scheduled_appointments')
    specialist = models.ForeignKey(Specialist, on_delete=models.SET_NULL, null=True, blank=True, related_name='concierge_appointments')
    wellness_plan = models.ForeignKey(WellnessPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='concierge_appointments')
    request = models.ForeignKey(ConciergeRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    
    # Appointment Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    appointment_type = models.CharField(max_length=30, choices=APPOINTMENT_TYPES)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS, default='scheduled')
    
    # Scheduling
    scheduled_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Location
    is_virtual = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)
    location = models.TextField(blank=True)
    
    # Preparation and Follow-up
    preparation_instructions = models.TextField(blank=True)
    post_appointment_notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.client.get_full_name()} on {self.scheduled_datetime.date()}"


class ConciergeNote(models.Model):
    """Notes and updates from concierge agents"""
    NOTE_TYPES = [
        ('general', 'General Note'),
        ('client_preference', 'Client Preference'),
        ('follow_up', 'Follow-up Required'),
        ('escalation', 'Escalation'),
        ('achievement', 'Client Achievement'),
        ('concern', 'Concern'),
        ('recommendation', 'Recommendation'),
    ]
    
    agent = models.ForeignKey(ConciergeAgent, on_delete=models.CASCADE, related_name='notes')
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='concierge_notes')
    request = models.ForeignKey(ConciergeRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    is_private = models.BooleanField(default=False, help_text="Only visible to concierge team")
    requires_action = models.BooleanField(default=False)
    action_due_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client.get_full_name()}"
