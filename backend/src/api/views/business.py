from rest_framework import viewsets, permissions
from api.models.business import BusinessIdea
from api.serializers.business import BusinessIdeaSerializer

class BusinessIdeaViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessIdeaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BusinessIdea.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
