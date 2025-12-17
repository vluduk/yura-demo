from django.urls import path
from api.views.settings import UserAssessmentSettingsView

urlpatterns = [
    path('settings/', UserAssessmentSettingsView.as_view(), name='user-settings'),
]
