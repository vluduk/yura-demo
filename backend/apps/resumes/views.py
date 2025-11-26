from rest_framework import generics, permissions
from .models import Resume, ResumeTemplate
from .serializers import ResumeSerializer, ResumeTemplateSerializer

class ResumeListCreateView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'
    lookup_url_kwarg = 'resume_id'

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

class TemplateListView(generics.ListAPIView):
    queryset = ResumeTemplate.objects.all()
    serializer_class = ResumeTemplateSerializer
    permission_classes = (permissions.AllowAny,)
