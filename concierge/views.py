from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ConciergeRequest, ConciergeService, ConciergeAppointment


@login_required
def concierge_dashboard(request):
    """Concierge dashboard"""
    recent_requests = ConciergeRequest.objects.filter(client=request.user).order_by('-created_at')[:5]
    upcoming_appointments = ConciergeAppointment.objects.filter(
        client=request.user,
        status='confirmed'
    ).order_by('scheduled_datetime')[:5]
    
    context = {
        'recent_requests': recent_requests,
        'upcoming_appointments': upcoming_appointments,
        'title': 'Concierge Dashboard',
    }
    return render(request, 'concierge/dashboard.html', context)


@login_required
def create_request(request):
    """Create concierge request"""
    if request.method == 'POST':
        # Handle request creation logic here
        messages.success(request, 'Your concierge request has been submitted!')
        return redirect('concierge:dashboard')
    
    services = ConciergeService.objects.filter(is_active=True)
    context = {
        'services': services,
        'title': 'Request Concierge Service',
    }
    return render(request, 'concierge/create_request.html', context)


@login_required
def request_list(request):
    """List user's concierge requests"""
    requests = ConciergeRequest.objects.filter(client=request.user).order_by('-created_at')
    
    context = {
        'requests': requests,
        'title': 'My Concierge Requests',
    }
    return render(request, 'concierge/request_list.html', context)


@login_required
def request_detail(request, pk):
    """Concierge request detail"""
    concierge_request = get_object_or_404(ConciergeRequest, pk=pk, client=request.user)
    
    context = {
        'request': concierge_request,
        'title': concierge_request.title,
    }
    return render(request, 'concierge/request_detail.html', context)


@login_required
def appointment_list(request):
    """List user's appointments"""
    appointments = ConciergeAppointment.objects.filter(client=request.user).order_by('-scheduled_datetime')
    
    context = {
        'appointments': appointments,
        'title': 'My Appointments',
    }
    return render(request, 'concierge/appointment_list.html', context)


def service_list(request):
    """List all concierge services"""
    services = ConciergeService.objects.filter(is_active=True).order_by('category', 'name')
    
    context = {
        'services': services,
        'title': 'Concierge Services',
    }
    return render(request, 'concierge/service_list.html', context)
