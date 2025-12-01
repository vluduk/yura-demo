from django.urls import path
from api.views.conversation import ConversationListCreateView, ConversationDetailView, ConversationChatView

urlpatterns = [
    path('conversations', ConversationListCreateView.as_view(), name='conversations-list-create'),
    path('conversations/chat', ConversationChatView.as_view(), name='conversations-chat'),
    path('conversations/<uuid:pk>', ConversationDetailView.as_view(), name='conversations-detail'),
]
