from django.urls import path
from . import views

app_name = 'wellness_plans'

urlpatterns = [
    path('', views.plan_list, name='list'),
    path('create/', views.create_plan, name='create'),
    path('<int:pk>/', views.plan_detail, name='detail'),
    path('<int:pk>/progress/', views.plan_progress, name='progress'),
    path('<int:pk>/sessions/', views.plan_sessions, name='sessions'),
    path('session/<int:session_id>/complete/', views.complete_session, name='complete_session'),
]