from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.file import UploadedFileViewSet

router = DefaultRouter()
router.register(r'files', UploadedFileViewSet, basename='file')

urlpatterns = [
    path('', include(router.urls)),
]
