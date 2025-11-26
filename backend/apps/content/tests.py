from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Article, ArticleCategory

User = get_user_model()

class ArticleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone='+3333333333', password='pass', name='Author', surname='One')
        self.client.force_authenticate(user=self.user)
        
        self.category = ArticleCategory.objects.create(name='Tech', slug='tech')
        
        self.article_data = {
            'title': 'Test Article',
            'slug': 'test-article',
            'content': 'Content of the article',
            'is_published': True,
            'category': self.category.id
        }
        self.article = Article.objects.create(author=self.user, category=self.category, title='Test Article', slug='test-article', content='Content', is_published=True)
        
        self.list_url = reverse('article-list')
        self.detail_url = reverse('article-detail', kwargs={'article_id': self.article.id})
        self.category_list_url = reverse('category-list')

    def test_create_article(self):
        data = self.article_data.copy()
        data['slug'] = 'new-unique-slug'
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)

    def test_list_articles(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_retrieve_article(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article.title)

    def test_update_article(self):
        data = {'title': 'Updated Article Title'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Article Title')

    def test_delete_article(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_create_category(self):
        data = {'name': 'New Cat', 'slug': 'new-cat'}
        response = self.client.post(self.category_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
