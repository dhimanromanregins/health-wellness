from django.contrib import admin
from .models import ConciergeAgent, ConciergeService, ConciergeRequest, ConciergeAppointment, ConciergeNote


@admin.register(ConciergeAgent)
class ConciergeAgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'total_clients', 'client_satisfaction_rating', 'is_active']
    list_filter = ['is_active', 'department']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'employee_id']
    raw_id_fields = ['user']


@admin.register(ConciergeService)
class ConciergeServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'minimum_tier', 'base_price', 'is_complimentary', 'is_active']
    list_filter = ['category', 'minimum_tier', 'is_complimentary', 'is_active']
    search_fields = ['name', 'description']


@admin.register(ConciergeRequest)
class ConciergeRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'agent', 'service', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'service__category']
    search_fields = ['title', 'description', 'client__email', 'client__first_name', 'client__last_name']
    raw_id_fields = ['client', 'agent', 'service']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('client', 'service', 'title', 'description', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('agent',)
        }),
        ('Scheduling', {
            'fields': ('preferred_date', 'deadline', 'estimated_completion')
        }),
        ('Details', {
            'fields': ('special_instructions', 'budget_range', 'location_preferences')
        }),
        ('Completion', {
            'fields': ('completed_at', 'completion_notes', 'client_rating', 'client_feedback'),
            'classes': ['collapse']
        }),
        ('Cost', {
            'fields': ('estimated_cost', 'actual_cost'),
            'classes': ['collapse']
        }),
    )


@admin.register(ConciergeAppointment)
class ConciergeAppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'agent', 'specialist', 'scheduled_datetime', 'status', 'appointment_type']
    list_filter = ['status', 'appointment_type', 'is_virtual']
    search_fields = ['title', 'client__email', 'specialist__user__first_name', 'specialist__user__last_name']
    raw_id_fields = ['client', 'agent', 'specialist', 'wellness_plan', 'request']


@admin.register(ConciergeNote)
class ConciergeNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'agent', 'client', 'note_type', 'requires_action', 'created_at']
    list_filter = ['note_type', 'requires_action', 'is_private']
    search_fields = ['title', 'content', 'client__email']
    raw_id_fields = ['agent', 'client', 'request']
