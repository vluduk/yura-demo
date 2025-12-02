from django.db import models
from django.conf import settings
import uuid


class ArticleCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        db_table = 'article_categories'

    def __str__(self):
        return self.name


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='articles')
    category = models.ForeignKey(ArticleCategory, on_delete=models.SET_NULL, null=True, related_name='articles')
    # Tags: many-to-many to ArticleTag (defined below)
    # Use blank=True to allow articles without tags
    # Related name 'articles' allows reverse lookup from tag to articles
    # Will be created in a migration to avoid requiring tag model before migrations
    tags = models.ManyToManyField('ArticleTag', blank=True, related_name='articles')
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    content = models.TextField()
    cover_image_url = models.CharField(max_length=500, blank=True, null=True)
    is_promoted = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'articles'

    def __str__(self):
        return self.title


class ArticleTag(models.Model):
    """Simple tag model for articles."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        db_table = 'article_tags'

    def __str__(self):
        return self.name
