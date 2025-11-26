from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Resume, ResumeTemplate

User = get_user_model()

class ResumeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='+5555555555', password='pass', name='Job', surname='Seeker')
        self.client.force_authenticate(user=self.user)
        
        self.template = ResumeTemplate.objects.create(name='Modern', structure={'layout': 'modern'})
        self.resume = Resume.objects.create(user=self.user, title='My Resume', template=self.template, data={})
        
        self.list_url = reverse('resume-list')
        self.create_url = reverse('resume-create')
        self.detail_url = reverse('resume-detail', kwargs={'resume_id': self.resume.id})
        self.template_list_url = reverse('template-list')

    def test_create_resume(self):
        data = {
            'title': 'New Resume',
            'template': self.template.id,
            'data': {'experience': []}
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resume.objects.count(), 2)

    def test_list_resumes(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_resume(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Resume')

    def test_update_resume(self):
        data = {'title': 'Updated Resume'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Resume')

    def test_delete_resume(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Resume.objects.filter(id=self.resume.id).exists())

    def test_list_templates(self):
        response = self.client.get(self.template_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
