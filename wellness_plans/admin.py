from django.contrib import admin
from .models import WellnessPlan, PlanModule, PlanSession, PlanProgress


@admin.register(WellnessPlan)
class WellnessPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'plan_type', 'status', 'difficulty_level', 'progress_percentage', 'created_at']
    list_filter = ['plan_type', 'status', 'difficulty_level']
    search_fields = ['title', 'user__email', 'user__first_name', 'user__last_name']
    filter_horizontal = ['specialists']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'plan_type', 'difficulty_level', 'status')
        }),
        ('Schedule', {
            'fields': ('duration_weeks', 'sessions_per_week', 'estimated_time_per_session', 'start_date', 'end_date')
        }),
        ('Goals & Targets', {
            'fields': ('primary_goals', 'target_metrics', 'success_criteria')
        }),
        ('Team', {
            'fields': ('specialists',)
        }),
        ('AI Configuration', {
            'fields': ('ai_model_version', 'personalization_factors', 'adaptation_rules'),
            'classes': ['collapse']
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'current_week', 'last_activity_date'),
            'classes': ['collapse']
        }),
    )


@admin.register(PlanModule)
class PlanModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'plan', 'module_type', 'order', 'is_mandatory', 'is_active']
    list_filter = ['module_type', 'is_mandatory', 'is_active']
    search_fields = ['title', 'description', 'plan__title']
    raw_id_fields = ['plan']
    ordering = ['plan', 'order']


@admin.register(PlanSession)
class PlanSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'plan', 'week_number', 'session_number', 'status', 'scheduled_date']
    list_filter = ['status', 'week_number', 'module__module_type']
    search_fields = ['title', 'description', 'plan__title']
    raw_id_fields = ['plan', 'module']
    ordering = ['plan', 'week_number', 'session_number']


@admin.register(PlanProgress)
class PlanProgressAdmin(admin.ModelAdmin):
    list_display = ['plan', 'date', 'week_number', 'weight', 'energy_level', 'mood_rating']
    list_filter = ['week_number', 'energy_level', 'mood_rating']
    search_fields = ['plan__title', 'plan__user__email']
    raw_id_fields = ['plan']
    ordering = ['-date']
