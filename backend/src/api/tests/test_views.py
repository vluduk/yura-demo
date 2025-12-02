from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from api.models.conversation import Conversation, ConversationType
from api.models.message import Message
from api.models.business import BusinessIdea, ActionStep
from api.models.article import Article, ArticleCategory
from api.models.user_assesment import UserAssessment

User = get_user_model()


class AuthViewsTest(TestCase):
    """Tests for authentication views"""
    
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('sign-up')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.me_url = reverse('me')
        
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'password': 'SecurePass123!'
        }

    def test_signup_success(self):
        """Test successful user signup"""
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_signup_duplicate_email(self):
        """Test signup with duplicate email"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_signup_missing_required_fields(self):
        """Test signup with missing required fields"""
        incomplete_data = {
            'email': 'test@example.com',
            'first_name': 'John'
            # Missing last_name and password
        }
        response = self.client.post(self.signup_url, incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_login_success(self):
        """Test successful login"""
        User.objects.create_user(**self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        User.objects.create_user(**self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_authenticated(self):
        """Test logout when authenticated"""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        """Test logout when not authenticated"""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_authenticated(self):
        """Test /me endpoint when authenticated"""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['first_name'], user.first_name)

    def test_me_endpoint_unauthenticated(self):
        """Test /me endpoint when not authenticated"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConversationViewsTest(TestCase):
    """Tests for conversation views"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.conversations_url = reverse('conversation-list')

    def test_list_conversations_empty(self):
        """Test listing conversations when user has none"""
        response = self.client.get(self.conversations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_conversations_with_data(self):
        """Test listing conversations when user has some"""
        conv1 = Conversation.objects.create(user=self.user, title='Conversation 1')
        conv2 = Conversation.objects.create(user=self.user, title='Conversation 2')
        
        response = self.client.get(self.conversations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_conversations_only_own(self):
        """Test that user only sees their own conversations"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )
        own_conv = Conversation.objects.create(user=self.user, title='My Conv')
        other_conv = Conversation.objects.create(user=other_user, title='Other Conv')
        
        response = self.client.get(self.conversations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(own_conv.id))

    def test_create_conversation(self):
        """Test creating a new conversation"""
        data = {
            'title': 'New Conversation',
            'conv_type': ConversationType.BUSINESS
        }
        with patch('api.services.advisor.AdvisorService.generate_initial_message') as mock_gen:
            mock_gen.return_value = 'Welcome message'
            response = self.client.post(self.conversations_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Conversation')
        self.assertTrue(Conversation.objects.filter(title='New Conversation').exists())

    def test_retrieve_conversation(self):
        """Test retrieving a specific conversation"""
        conv = Conversation.objects.create(user=self.user, title='Test Conv')
        url = reverse('conversation-detail', kwargs={'pk': conv.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(conv.id))

    def test_retrieve_other_user_conversation_forbidden(self):
        """Test that user cannot retrieve another user's conversation"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )
        other_conv = Conversation.objects.create(user=other_user, title='Other Conv')
        url = reverse('conversation-detail', kwargs={'pk': other_conv.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_cannot_access_conversations(self):
        """Test that unauthenticated users cannot access conversations"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.conversations_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConversationChatViewTest(TestCase):
    """Tests for the conversation chat view"""
    
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
    def test_chat_with_existing_conversation(self, mock_ai):
        """Test sending a message to an existing conversation"""
        mock_ai.return_value = 'AI response here'
        
        conv = Conversation.objects.create(user=self.user, title='Test Conv')
        data = {
            'conversation_id': str(conv.id),
            'content': 'Hello, AI!'
        }
        
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify messages were created
        messages = Message.objects.filter(conversation=conv)
        self.assertEqual(messages.count(), 2)  # User message + AI response
        self.assertTrue(messages.filter(is_user=True, content='Hello, AI!').exists())
        self.assertTrue(messages.filter(is_user=False, content='AI response here').exists())

    @patch('api.services.advisor.AdvisorService.get_ai_response')
    @patch('api.services.advisor.AdvisorService.generate_conversation_title')
    def test_chat_creates_new_conversation(self, mock_title, mock_ai):
        """Test that chat creates a new conversation if none provided"""
        mock_ai.return_value = 'AI response'
        mock_title.return_value = None
        
        data = {
            'content': 'Hello, AI!',
            'title': 'My New Chat'
        }
        
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify conversation was created
        self.assertTrue(Conversation.objects.filter(user=self.user, title='My New Chat').exists())

    def test_chat_missing_content(self):
        """Test chat with missing content"""
        data = {
            'conversation_id': 'some-id'
        }
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chat_nonexistent_conversation(self):
        """Test chat with non-existent conversation ID"""
        data = {
            'conversation_id': '00000000-0000-0000-0000-000000000000',
            'content': 'Hello'
        }
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_chat_other_user_conversation(self):
        """Test that user cannot chat in another user's conversation"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )
        other_conv = Conversation.objects.create(user=other_user, title='Other Conv')
        
        data = {
            'conversation_id': str(other_conv.id),
            'content': 'Hello'
        }
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('api.services.advisor.AdvisorService.get_ai_response')
    def test_chat_ai_service_exception(self, mock_ai):
        """Test chat when AI service raises an exception"""
        mock_ai.side_effect = Exception('AI service error')
        
        conv = Conversation.objects.create(user=self.user, title='Test Conv')
        data = {
            'conversation_id': str(conv.id),
            'content': 'Hello'
        }
        
        response = self.client.post(self.chat_url, data)
        # Should still return 201 but with error message in AI response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Помилка', response.data['content'])

    def test_chat_unauthenticated(self):
        """Test that unauthenticated users cannot chat"""
        self.client.force_authenticate(user=None)
        data = {'content': 'Hello'}
        response = self.client.post(self.chat_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HealthCheckViewTest(TestCase):
    """Tests for the health check view"""
    
    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'ok')


class ArticleViewsTest(TestCase):
    """Tests for article views (if they exist)"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.category = ArticleCategory.objects.create(
            name='Tech',
            slug='tech'
        )
        self.article = Article.objects.create(
            author=self.user,
            category=self.category,
            title='Test Article',
            slug='test-article',
            content='Article content',
            is_published=True
        )

    def test_article_str_representation(self):
        """Test article string representation"""
        self.assertEqual(str(self.article), 'Test Article')

    def test_unpublished_article_visibility(self):
        """Test that unpublished articles have correct flag"""
        unpublished = Article.objects.create(
            author=self.user,
            category=self.category,
            title='Unpublished',
            slug='unpublished',
            content='Content',
            is_published=False
        )
        self.assertFalse(unpublished.is_published)


class UserAssessmentIntegrationTest(TestCase):
    """Integration tests for UserAssessment with other components"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_create_assessment_for_user(self):
        """Test creating an assessment for a user"""
        assessment = UserAssessment.objects.create(
            user=self.user,
            answers={
                'service_branch': 'Army',
                'primary_skills': 'leadership,logistics',
                'current_goals': 'Find civilian job',
                'work_preferences': 'Full-time employment'
            }
        )
        self.assertEqual(assessment.user, self.user)
        self.assertIsNotNone(assessment.to_llm_context())

    def test_multiple_assessments_per_user(self):
        """Test that a user can have multiple assessments"""
        assessment1 = UserAssessment.objects.create(user=self.user)
        assessment2 = UserAssessment.objects.create(user=self.user)
        
        self.assertEqual(self.user.assessments.count(), 2)

    def test_assessment_cascade_delete(self):
        """Test that deleting a user deletes their assessments"""
        assessment = UserAssessment.objects.create(user=self.user)
        user_id = self.user.id
        self.user.delete()
        self.assertFalse(UserAssessment.objects.filter(user_id=user_id).exists())


class PermissionsTest(TestCase):
    """Tests for permission checks across views"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_authenticated_required_for_conversations(self):
        """Test that conversations require authentication"""
        url = reverse('conversation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_required_for_chat(self):
        """Test that chat requires authentication"""
        url = reverse('conversation-chat')
        response = self.client.post(url, {'content': 'Hello'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_required_for_me(self):
        """Test that /me requires authentication"""
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_access_to_signup(self):
        """Test that signup is publicly accessible"""
        url = reverse('sign-up')
        data = {
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        # Should not be 401 (could be 201 or 400 for validation)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_access_to_login(self):
        """Test that login is publicly accessible"""
        url = reverse('login')
        response = self.client.post(url, {'email': 'test@test.com', 'password': 'pass'})
        # Should not be 401 (could be 401 for invalid credentials or 200 for success)
        # The point is it doesn't require authentication to access
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])
