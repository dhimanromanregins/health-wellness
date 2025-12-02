from django.contrib import admin
from .models import SpecialistCategory, Specialist, SpecialistReview, SpecialistAvailability


@admin.register(SpecialistCategory)
class SpecialistCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['display_name', 'description']


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'tier', 'years_experience', 'average_rating', 'is_verified', 'is_accepting_clients']
    list_filter = ['tier', 'is_verified', 'is_featured', 'is_accepting_clients']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'specializations']
    filter_horizontal = ['categories']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'categories', 'professional_summary')
        }),
        ('Experience', {
            'fields': ('years_experience', 'tier', 'certifications', 'education', 'specializations')
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'consultation_rate', 'timezone')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_featured', 'is_accepting_clients')
        }),
        ('Metrics', {
            'fields': ('total_clients', 'average_rating', 'total_reviews', 'success_rate'),
            'classes': ['collapse']
        }),
    )


@admin.register(SpecialistReview)
class SpecialistReviewAdmin(admin.ModelAdmin):
    list_display = ['specialist', 'client', 'rating', 'is_verified', 'is_public', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_public']
    search_fields = ['specialist__user__first_name', 'specialist__user__last_name', 'client__first_name', 'client__last_name']
    raw_id_fields = ['specialist', 'client']


@admin.register(SpecialistAvailability)
class SpecialistAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['specialist', 'get_day_of_week_display', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    raw_id_fields = ['specialist']
