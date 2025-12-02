from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Specialist, SpecialistCategory, SpecialistReview


def specialist_list(request):
    """List all specialists"""
    specialists = Specialist.objects.filter(is_accepting_clients=True).select_related('user')
    categories = SpecialistCategory.objects.filter(is_active=True)
    
    context = {
        'specialists': specialists,
        'categories': categories,
        'title': 'Curated Specialists',
    }
    return render(request, 'specialists/list.html', context)


def specialist_detail(request, pk):
    """Specialist detail view"""
    specialist = get_object_or_404(Specialist, pk=pk)
    reviews = SpecialistReview.objects.filter(specialist=specialist, is_public=True).select_related('client')[:10]
    
    context = {
        'specialist': specialist,
        'reviews': reviews,
        'title': f'{specialist.get_full_name()}',
    }
    return render(request, 'specialists/detail.html', context)


def specialists_by_category(request, category):
    """Filter specialists by category"""
    try:
        category_obj = SpecialistCategory.objects.get(name=category, is_active=True)
        specialists = Specialist.objects.filter(
            categories=category_obj, 
            is_accepting_clients=True
        ).select_related('user')
    except SpecialistCategory.DoesNotExist:
        specialists = Specialist.objects.none()
        category_obj = None
    
    context = {
        'specialists': specialists,
        'category': category_obj,
        'title': f'{category_obj.display_name if category_obj else "Category"} Specialists',
    }
    return render(request, 'specialists/list.html', context)


@login_required
def book_specialist(request, specialist_id):
    """Book a specialist"""
    specialist = get_object_or_404(Specialist, id=specialist_id)
    
    if request.method == 'POST':
        # Handle booking logic here
        messages.success(request, f'Booking request sent to {specialist.get_full_name()}!')
        return JsonResponse({'success': True, 'message': 'Booking requested successfully'})
    
    context = {
        'specialist': specialist,
        'title': f'Book {specialist.get_full_name()}',
    }
    return render(request, 'specialists/book.html', context)


def specialist_reviews(request, specialist_id):
    """Specialist reviews"""
    specialist = get_object_or_404(Specialist, id=specialist_id)
    reviews = SpecialistReview.objects.filter(specialist=specialist, is_public=True).select_related('client')
    
    context = {
        'specialist': specialist,
        'reviews': reviews,
        'title': f'Reviews for {specialist.get_full_name()}',
    }
    return render(request, 'specialists/reviews.html', context)
