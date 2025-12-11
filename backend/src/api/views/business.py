from rest_framework import viewsets, permissions
from api.models.business import BusinessIdea
from api.serializers.business import BusinessIdeaSerializer
from drf_yasg.utils import swagger_auto_schema


class BusinessIdeaViewSet(viewsets.ModelViewSet):
    """ViewSet for managing business ideas.
    
    Provides full CRUD operations for business idea management.
    """
    serializer_class = BusinessIdeaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only business ideas owned by the authenticated user."""
        return BusinessIdea.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        """Create a business idea owned by the authenticated user."""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=['Business Ideas'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Business Ideas'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Business Ideas'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Business Ideas'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Business Ideas'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Business Ideas'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
