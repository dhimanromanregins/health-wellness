from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Registration API endpoints (3-step process)
    path('register/', views.initiate_registration, name='initiate_registration'),
    path('register/verify/', views.verify_registration_otp, name='verify_registration_otp'),
    path('register/complete/', views.complete_registration, name='complete_registration'),
    
    # Authentication endpoints
    path('login/', views.login, name='login'),
    path('login/otp/', views.login_with_otp, name='login_with_otp'),
    path('logout/', views.logout, name='logout'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    
    # User profile endpoints
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/class-based/', views.UserProfileView.as_view(), name='user_profile_class'),
    
    # Onboarding
    path('onboarding/complete/', views.complete_onboarding, name='complete_onboarding'),
    
    # Demo/Development endpoints
    path('demo/login/', views.demo_login, name='demo_login'),
]