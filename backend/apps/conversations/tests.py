from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

class ConversationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='+4444444444', password='pass', name='Chat', surname='User')
        self.client.force_authenticate(user=self.user)
        
        self.conversation = Conversation.objects.create(user=self.user, title='Test Chat')
        self.create_url = reverse('conversation-create')
        self.list_url = reverse('conversation-list')
        self.detail_url = reverse('conversation-detail', kwargs={'conversation_id': self.conversation.id})

    def test_create_conversation(self):
        data = {'title': 'New Conversation'}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)

    def test_list_conversations(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_conversation(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('messages', response.data)

    def test_send_message(self):
        url = reverse('message-create', kwargs={'conversation_id': self.conversation.id})
        data = {'request': 'Hello AI'}
        # The view returns StreamingHttpResponse, which might be tricky to test with standard client.
        # We check if it returns 200 OK and creates a message.
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Message.objects.filter(conversation=self.conversation, content='Hello AI').exists())
