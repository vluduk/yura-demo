from rest_framework import serializers
from api.models.article import Article, ArticleCategory


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ('id', 'name', 'slug')


class ArticleSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source='author', read_only=True)
    category = ArticleCategorySerializer(read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'author_id', 'category', 'title', 'slug', 'content', 'cover_image_url', 'is_promoted', 'is_published', 'views_count', 'created_at')
        read_only_fields = ('id', 'author_id', 'views_count', 'created_at')
