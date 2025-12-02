from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from api.models.conversation import Conversation, ConversationType
from api.models.message import Message

User = get_user_model()

class ConversationTitleTest(TestCase):
    """Tests for conversation title generation logic"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.chat_url = reverse('conversation-chat')

    @patch('api.services.advisor.AdvisorService.get_ai_response')
    def test_default_title_business(self, mock_ai):
        """Test default title for Business conversation"""
        mock_ai.return_value = 'AI response'
        
        data = {
            'content': 'Hello',
            'conv_type': ConversationType.BUSINESS
        }
        
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        conv = Conversation.objects.get(user=self.user)
        self.assertEqual(conv.title, 'Власний бізнес - новий чат')

    @patch('api.services.advisor.AdvisorService.get_ai_response')
    def test_default_title_hiring(self, mock_ai):
        """Test default title for Hiring conversation"""
        mock_ai.return_value = 'AI response'
        
        data = {
            'content': 'Hello',
            'conv_type': ConversationType.HIRING
        }
        
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        conv = Conversation.objects.get(user=self.user)
        self.assertEqual(conv.title, 'Наймана праця - новий чат')

    @patch('api.services.advisor.AdvisorService.get_ai_response')
    def test_default_title_general(self, mock_ai):
        """Test default title for conversation without type"""
        mock_ai.return_value = 'AI response'
        
        data = {
            'content': 'Hello'
        }
        
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        conv = Conversation.objects.get(user=self.user)
        # 'Загальна' is the fallback label we used
        self.assertEqual(conv.title, 'Загальна - новий чат')

    @patch('api.services.advisor.AdvisorService.get_ai_response')
    @patch('api.services.advisor.AdvisorService.generate_conversation_title')
    def test_title_generation_trigger(self, mock_gen_title, mock_ai):
        """Test that title generation is triggered only after enough messages"""
        mock_ai.return_value = 'AI response'
        
        # Create conversation with default title
        conv = Conversation.objects.create(
            user=self.user,
            title='Власний бізнес - новий чат',
            conv_type=ConversationType.BUSINESS
        )
        
        # 1. Add 1st user message (total 2 messages: 1 user + 1 AI)
        # We already have 0 messages.
        # Calling chat endpoint adds 1 user msg + 1 AI msg.
        
        data = {
            'conversation_id': str(conv.id),
            'content': 'Message 1'
        }
        self.client.post(self.chat_url, data)
        
        # Total messages: 2. Should NOT trigger generation.
        mock_gen_title.assert_not_called()
        
        # 2. Add 2nd user message (total 4 messages)
        self.client.post(self.chat_url, data)
        
        # Total messages: 4. Should TRIGGER generation.
        mock_gen_title.assert_called_once_with(conv)

    @patch('api.services.advisor.AdvisorService.get_ai_response')
    @patch('api.services.advisor.AdvisorService.generate_conversation_title')
    def test_title_generation_not_triggered_if_custom_title(self, mock_gen_title, mock_ai):
        """Test that title generation is NOT triggered if title is already custom"""
        mock_ai.return_value = 'AI response'
        
        conv = Conversation.objects.create(
            user=self.user,
            title='My Custom Title',
            conv_type=ConversationType.BUSINESS
        )
        
        data = {
            'conversation_id': str(conv.id),
            'content': 'Message 1'
        }
        
        # Add messages until we reach threshold
        self.client.post(self.chat_url, data) # 2 msgs
        self.client.post(self.chat_url, data) # 4 msgs
        
        # Should NOT trigger because title is not default
        mock_gen_title.assert_not_called()
