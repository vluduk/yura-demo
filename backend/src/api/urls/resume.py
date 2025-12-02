from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.resume import ResumeViewSet, CVTemplateViewSet

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'cv-templates', CVTemplateViewSet, basename='cv-template')

urlpatterns = [
    path('', include(router.urls)),
]
