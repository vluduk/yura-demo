from rest_framework import generics, permissions
from .models import BusinessIdea
from .serializers import BusinessIdeaSerializer

class IdeaListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessIdeaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Swagger says /ideas/me for list, and /ideas for create?
        # Actually swagger has /ideas/me (GET) and /ideas (POST).
        # But standard REST usually combines list/create.
        # I will support both on /ideas if needed, or stick to swagger strictly.
        # Swagger: /ideas/me -> GET list. /ideas -> POST create.
        return BusinessIdea.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IdeaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessIdeaSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'
    lookup_url_kwarg = 'idea_id'

    def get_queryset(self):
        return BusinessIdea.objects.filter(user=self.request.user)
