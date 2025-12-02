from rest_framework import serializers
from api.models.article import Article, ArticleCategory
from api.models.article import ArticleTag


class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ('id', 'name', 'slug')


class ArticleSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(source='author', read_only=True)
    category = ArticleCategorySerializer(read_only=True)
    summary = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'author_id', 'category', 'title', 'slug', 'content', 'summary', 'tags', 'cover_image_url', 'is_promoted', 'is_published', 'views_count', 'created_at')
        read_only_fields = ('id', 'author_id', 'views_count', 'created_at')

    def get_summary(self, obj):
        # Return first 200 chars of content as summary
        if obj.content:
            return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content
        return ""

    def get_tags(self, obj):
        # Return list of tag names
        try:
            return [t.name for t in obj.tags.all()]
        except Exception:
            return []
