from rest_framework import viewsets, permissions, status
import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models.resume import Resume
from api.serializers.resume import ResumeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    logger = logging.getLogger(__name__)

    def create(self, request, *args, **kwargs):
        """Override create to log serializer validation errors for debugging."""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Log full error details to help debugging frequent 400s
            self.logger.warning("Resume create validation errors: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save with the authenticated user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

# CVTemplate endpoints removed — templates are now maintained on the frontend.
