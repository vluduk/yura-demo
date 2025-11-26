from django.urls import path
from .views import ConversationListCreateView, ConversationDetailView, MessageCreateView, MessageActionView

urlpatterns = [
    path('', ConversationListCreateView.as_view(), name='conversation-create'), # POST /conversations
    path('me', ConversationListCreateView.as_view(), name='conversation-list'), # GET /conversations/me
    path('<uuid:conversation_id>', ConversationDetailView.as_view(), name='conversation-detail'),
    path('<uuid:conversation_id>/messages', MessageCreateView.as_view(), name='message-create'),
    path('<uuid:conversation_id>/messages/<uuid:messages_id>', MessageActionView.as_view(), name='message-action'),
]
