from django.urls import path
from . import views

app_name = 'concierge'

urlpatterns = [
    path('', views.concierge_dashboard, name='dashboard'),
    path('request/', views.create_request, name='create_request'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('services/', views.service_list, name='service_list'),
]