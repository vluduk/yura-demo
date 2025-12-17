from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
from api.models.resume import Resume
from api.serializers.resume import ResumeSerializer
from api.services.resume_ai_service import ResumeAIService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ResumeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing resumes.
    
    Provides full CRUD operations plus AI suggestion functionality.
    """
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    logger = logging.getLogger(__name__)

    def get_queryset(self):
        """Return only resumes owned by the authenticated user."""
        return Resume.objects.filter(user=self.request.user).order_by('-updated_at')

    @action(detail=False, methods=['post'], url_path='generate-summary')
    def generate_summary(self, request):
        """Generate a resume summary using AI."""
        try:
            resume_data = request.data.get('resume_data', {})
            instructions = request.data.get('instructions', '')
            
            summary = ResumeAIService.generate_summary(
                user=request.user,
                resume_data=resume_data,
                extra_instructions=instructions
            )
            
            return Response({'summary': summary}, status=status.HTTP_200_OK)
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return Response(
                {'error': 'Failed to generate summary. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        """Create a resume owned by the authenticated user."""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(tags=['Resumes'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Resumes'])
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

    @swagger_auto_schema(tags=['Resumes'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Resumes'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Resumes'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Resumes'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='ai-suggest')
    @swagger_auto_schema(
        tags=['Resumes', 'AI'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['field'],
            properties={
                'field': openapi.Schema(type=openapi.TYPE_STRING, description='Field to generate content for'),
                'context': openapi.Schema(type=openapi.TYPE_STRING, description='Optional context for generation'),
            },
        ),
        responses={
            200: openapi.Response('AI-generated content', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'content': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            400: 'Bad request - field is required'
        }
    )
    def ai_suggest(self, request, pk=None):
        """Generate AI content for a specific field in the resume.
        
        Request body:
        - field: The field to generate content for (required)
        - context: Optional context to help with generation
        """
        resume = self.get_object()
        field = request.data.get('field')
        context = request.data.get('context')
        
        if not field:
            return Response({'error': 'Field is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        from api.services.advisor import AdvisorService
        content = AdvisorService.generate_resume_content(request.user, resume, field, context)
        
        return Response({'content': content})
