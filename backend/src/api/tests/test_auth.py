from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.role, 'USER')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        self.assertEqual(admin.email, 'admin@example.com')
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, 'ADMIN')

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='password123')


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('sign-up')
        self.login_url = reverse('login')
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '0991234567',
            'password': 'HardPassword123'
        }

    def test_signup_success(self):
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check cookies instead of response body
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_signup_duplicate_email(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.signup_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_login_success(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check cookies instead of response body
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_login_invalid_credentials(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
