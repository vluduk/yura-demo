from django.urls import path
from .views import IdeaListCreateView, IdeaDetailView

urlpatterns = [
    path('me', IdeaListCreateView.as_view(), name='idea-list'), # GET /ideas/me
    path('', IdeaListCreateView.as_view(), name='idea-create'), # POST /ideas
    path('<uuid:idea_id>', IdeaDetailView.as_view(), name='idea-detail'),
]
