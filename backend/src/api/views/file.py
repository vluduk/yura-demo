from rest_framework import viewsets, permissions, parsers, status
from rest_framework.response import Response
from api.models.file import UploadedFile
from api.serializers.file import UploadedFileSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UploadedFileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing uploaded files.
    
    Provides full CRUD operations for file uploads.
    Users can only access their own uploaded files.
    """
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        """Return only files uploaded by the authenticated user."""
        return UploadedFile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a file upload owned by the authenticated user."""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=['Files'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Files'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Files'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Files'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Files'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Files'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
