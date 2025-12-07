# wellness_hub/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Wellness Hub API",
        default_version='v1',
        description="API documentation for Wellness Hub application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@wellnesshub.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/core/', include('core.urls')),
    path('api/concierge/', include('concierge.urls')),
    path('api/specialists/', include('specialists.urls')),
    path('api/wellness-plans/', include('wellness_plans.urls')),
    
    # Swagger URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]