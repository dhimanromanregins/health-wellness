from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication URLs
    # path('', views.home_view, name='home'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    # path('signup/', views.SignUpView.as_view(), name='signup'),
    
    # # User dashboard and profile
    # path('dashboard/', views.dashboard_view, name='dashboard'),
    # path('profile/', views.profile_view, name='profile'),
    # path('delete-account/', views.delete_account_view, name='delete_account'),
    
    # # AJAX endpoints
    # path('api/update-profile/', views.update_profile_ajax, name='update_profile_ajax'),
]