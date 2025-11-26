from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Yura API",
      default_version='v1',
      description="API documentation for Yura application",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/users/', include('users.urls_users')), # Splitting for clarity if needed, or keep in one
    path('api/v1/ideas/', include('ideas.urls')),
    path('api/v1/articles/', include('content.urls')),
    path('api/v1/conversations/', include('conversations.urls')),
    path('api/v1/resumes/', include('resumes.urls')),
    
    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
