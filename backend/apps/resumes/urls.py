from django.urls import path
from .views import ResumeListCreateView, ResumeDetailView, TemplateListView

urlpatterns = [
    path('me', ResumeListCreateView.as_view(), name='resume-list'), # GET /resumes/me
    path('', ResumeListCreateView.as_view(), name='resume-create'), # POST /resumes
    path('<uuid:resume_id>', ResumeDetailView.as_view(), name='resume-detail'),
    path('templates', TemplateListView.as_view(), name='template-list'),
]
