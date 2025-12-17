from rest_framework import generics, permissions, status
from rest_framework.response import Response
from api.models.user_assesment import UserAssessment
from api.serializers.user_assessment import UserAssessmentSerializer


class UserAssessmentSettingsView(generics.RetrieveUpdateAPIView):
    """View for managing user assessment settings (language preferences, etc.)"""
    serializer_class = UserAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Get or create assessment for the current user."""
        assessment, _ = UserAssessment.objects.get_or_create(user=self.request.user)
        return assessment

    def patch(self, request, *args, **kwargs):
        """Update only specific settings fields."""
        assessment = self.get_object()
        
        # Only allow updating specific settings fields
        allowed_fields = ['preferred_language']
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        for field, value in update_data.items():
            setattr(assessment, field, value)
        
        assessment.save()
        serializer = self.get_serializer(assessment)
        return Response(serializer.data)
