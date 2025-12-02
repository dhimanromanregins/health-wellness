from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import WellnessPlan, PlanSession, PlanProgress


@login_required
def plan_list(request):
    """List user's wellness plans"""
    plans = WellnessPlan.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'plans': plans,
        'title': 'My Wellness Plans',
    }
    return render(request, 'wellness_plans/list.html', context)


@login_required
def create_plan(request):
    """Create a new wellness plan"""
    if request.method == 'POST':
        # Handle plan creation logic here
        messages.success(request, 'Your wellness plan has been created!')
        return redirect('wellness_plans:list')
    
    context = {
        'title': 'Create Wellness Plan',
    }
    return render(request, 'wellness_plans/create.html', context)


@login_required
def plan_detail(request, pk):
    """Wellness plan detail view"""
    plan = get_object_or_404(WellnessPlan, pk=pk, user=request.user)
    
    context = {
        'plan': plan,
        'title': plan.title,
    }
    return render(request, 'wellness_plans/detail.html', context)


@login_required
def plan_progress(request, pk):
    """Plan progress tracking"""
    plan = get_object_or_404(WellnessPlan, pk=pk, user=request.user)
    progress_entries = PlanProgress.objects.filter(plan=plan).order_by('-date')[:30]
    
    context = {
        'plan': plan,
        'progress_entries': progress_entries,
        'title': f'{plan.title} - Progress',
    }
    return render(request, 'wellness_plans/progress.html', context)


@login_required
def plan_sessions(request, pk):
    """Plan sessions view"""
    plan = get_object_or_404(WellnessPlan, pk=pk, user=request.user)
    sessions = PlanSession.objects.filter(plan=plan).order_by('week_number', 'session_number')
    
    context = {
        'plan': plan,
        'sessions': sessions,
        'title': f'{plan.title} - Sessions',
    }
    return render(request, 'wellness_plans/sessions.html', context)


@login_required
def complete_session(request, session_id):
    """Complete a session"""
    session = get_object_or_404(PlanSession, id=session_id, plan__user=request.user)
    
    if request.method == 'POST':
        session.status = 'completed'
        session.save()
        messages.success(request, f'Session "{session.title}" marked as completed!')
        return JsonResponse({'success': True, 'message': 'Session completed'})
    
    context = {
        'session': session,
        'title': f'Complete Session: {session.title}',
    }
    return render(request, 'wellness_plans/complete_session.html', context)
