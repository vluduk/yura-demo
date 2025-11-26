from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse('sign-up')
        self.login_url = reverse('login')
        self.user_me_url = reverse('user-me')
        
        self.user_data = {
            'phone': '+1234567890',
            'password': 'testpassword123',
            'name': 'Test',
            'surname': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_signup(self):
        data = {
            'phone': '+0987654321',
            'password': 'newpassword123',
            'name': 'New',
            'surname': 'User'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data)
        self.assertIn('refreshToken', response.data)

    def test_signup_invalid_data(self):
        data = {
            'phone': '', # Invalid
            'password': 'newpassword123'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        data = {
            'phone': self.user_data['phone'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'phone': self.user_data['phone'],
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_me(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], self.user_data['phone'])

    def test_get_user_me_unauthenticated(self):
        response = self.client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
