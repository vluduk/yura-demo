from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import BusinessIdea

User = get_user_model()

class BusinessIdeaTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='+1111111111', password='testpass', name='Idea', surname='Owner')
        self.other_user = User.objects.create_user(phone='+2222222222', password='testpass', name='Other', surname='User')
        
        self.client.force_authenticate(user=self.user)
        
        self.idea_data = {
            'title': 'Test Idea',
            'status': 'draft' # Note: 'draft' is not in choices, should be 'BRAINSTORM' but let's see if it validates. 
            # Actually choices are enforced at validation level usually, but model level if full_clean is called.
            # Let's use a valid choice 'BRAINSTORM' to be safe.
        }
        self.idea = BusinessIdea.objects.create(user=self.user, title='Test Idea', status='BRAINSTORM')
        
        self.list_url = reverse('idea-list') # /ideas/me
        self.create_url = reverse('idea-create') # /ideas/
        self.detail_url = reverse('idea-detail', kwargs={'idea_id': self.idea.id})

    def test_create_idea(self):
        data = {
            'title': 'New Idea',
            'status': 'VALIDATION'
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessIdea.objects.count(), 2)
        self.assertEqual(BusinessIdea.objects.get(id=response.data['id']).user, self.user)

    def test_list_ideas(self):
        # Create an idea for other user
        BusinessIdea.objects.create(user=self.other_user, title='Other Idea', status='BRAINSTORM')
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see own ideas
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Idea')

    def test_retrieve_idea(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Idea')

    def test_update_idea(self):
        data = {'title': 'Updated Title'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_delete_idea(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BusinessIdea.objects.filter(id=self.idea.id).count(), 0)

    def test_access_other_user_idea(self):
        other_idea = BusinessIdea.objects.create(user=self.other_user, title='Other', status='BRAINSTORM')
        url = reverse('idea-detail', kwargs={'idea_id': other_idea.id})
        response = self.client.get(url)
        # Should return 404 because queryset filters by request.user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
