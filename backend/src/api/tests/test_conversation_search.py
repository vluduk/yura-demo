from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from api.models.conversation import Conversation, ConversationType
from api.models.message import Message

User = get_user_model()


class ConversationListSearchTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test-search@example.com",
            password="HardPassword123",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("conversation-list")

    def test_list_supports_search_in_title_and_messages(self):
        conv1 = Conversation.objects.create(user=self.user, title="Business planning", conv_type=ConversationType.BUSINESS)
        conv2 = Conversation.objects.create(user=self.user, title="Hiring plan", conv_type=ConversationType.HIRING)

        Message.objects.create(conversation=conv2, content="We should hire an Angular developer", is_user=True)

        resp = self.client.get(self.url, {"search": "Angular", "page": 1, "limit": 20})
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

        ids = {item["id"] for item in resp.json()}
        self.assertIn(str(conv2.id), ids)
        self.assertNotIn(str(conv1.id), ids)

        # List responses should be lightweight (no messages payload)
        self.assertNotIn("messages", resp.json()[0])

    def test_list_supports_type_filter(self):
        conv1 = Conversation.objects.create(user=self.user, title="Business 1", conv_type=ConversationType.BUSINESS)
        conv2 = Conversation.objects.create(user=self.user, title="Hiring 1", conv_type=ConversationType.HIRING)

        resp = self.client.get(self.url, {"type": ConversationType.HIRING, "page": 1, "limit": 50})
        self.assertEqual(resp.status_code, 200)

        ids = {item["id"] for item in resp.json()}
        self.assertIn(str(conv2.id), ids)
        self.assertNotIn(str(conv1.id), ids)

    def test_list_paginates_with_page_and_limit(self):
        for i in range(25):
            Conversation.objects.create(user=self.user, title=f"Chat {i}", conv_type=ConversationType.BUSINESS)

        resp_page1 = self.client.get(self.url, {"page": 1, "limit": 20})
        resp_page2 = self.client.get(self.url, {"page": 2, "limit": 20})

        self.assertEqual(resp_page1.status_code, 200)
        self.assertEqual(resp_page2.status_code, 200)

        self.assertEqual(len(resp_page1.json()), 20)
        self.assertEqual(len(resp_page2.json()), 5)
