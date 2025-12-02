from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.platform_home, name='home'),
    path('subscription/', views.subscription_management, name='subscription'),
    path('notifications/', views.notification_center, name='notifications'),
    path('faq/', views.faq_list, name='faq'),
    path('api/notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]