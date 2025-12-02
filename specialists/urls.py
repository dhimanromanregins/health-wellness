from django.urls import path
from . import views

app_name = 'specialists'

urlpatterns = [
    path('', views.specialist_list, name='list'),
    path('<int:pk>/', views.specialist_detail, name='detail'),
    path('category/<str:category>/', views.specialists_by_category, name='by_category'),
    path('book/<int:specialist_id>/', views.book_specialist, name='book'),
    path('reviews/<int:specialist_id>/', views.specialist_reviews, name='reviews'),
]