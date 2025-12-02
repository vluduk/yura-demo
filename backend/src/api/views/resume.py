from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models.resume import Resume, CVTemplate
from api.serializers.resume import ResumeSerializer, CVTemplateSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='ai-suggest')
    def ai_suggest(self, request, pk=None):
        """
        Generate AI content for a specific field in the resume.
        """
        resume = self.get_object()
        field = request.data.get('field')
        context = request.data.get('context')
        
        if not field:
            return Response({'error': 'Field is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        from api.services.advisor import AdvisorService
        content = AdvisorService.generate_resume_content(request.user, resume, field, context)
        
        return Response({'content': content})

class CVTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CVTemplate.objects.filter(is_active=True)
    serializer_class = CVTemplateSerializer
    permission_classes = [permissions.AllowAny]
