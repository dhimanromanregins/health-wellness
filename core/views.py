from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Platform, Notification, FAQ, SubscriptionTier, UserSubscription


def platform_home(request):
    """Platform home page"""
    platform = Platform.objects.first()
    subscription_tiers = SubscriptionTier.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'platform': platform,
        'subscription_tiers': subscription_tiers,
        'title': 'VELORA - Premium Wellness Platform',
    }
    return render(request, 'core/home.html', context)


@login_required
def subscription_management(request):
    """Manage user subscription"""
    try:
        subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        subscription = None
    
    subscription_tiers = SubscriptionTier.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'subscription': subscription,
        'subscription_tiers': subscription_tiers,
        'title': 'Subscription Management',
    }
    return render(request, 'core/subscription.html', context)


@login_required
def notification_center(request):
    """User notification center"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'title': 'Notifications',
    }
    return render(request, 'core/notifications.html', context)


def faq_list(request):
    """FAQ page"""
    faqs = FAQ.objects.filter(is_published=True).order_by('category', 'sort_order')
    
    # Group FAQs by category
    faq_by_category = {}
    for faq in faqs:
        category = faq.get_category_display()
        if category not in faq_by_category:
            faq_by_category[category] = []
        faq_by_category[category].append(faq)
    
    context = {
        'faq_by_category': faq_by_category,
        'title': 'Frequently Asked Questions',
    }
    return render(request, 'core/faq.html', context)


@login_required
def mark_notifications_read(request):
    """Mark notifications as read via AJAX"""
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids[]')
        if notification_ids:
            Notification.objects.filter(
                id__in=notification_ids,
                user=request.user
            ).update(is_read=True)
            return JsonResponse({'success': True, 'message': 'Notifications marked as read'})
        else:
            # Mark all as read
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            return JsonResponse({'success': True, 'message': 'All notifications marked as read'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
