from rest_framework import serializers
from .models import Article, ArticleCategory, KnowledgeDocument, KnowledgeCategory

class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    category_details = ArticleCategorySerializer(source='category', read_only=True)

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'views_count', 'author')

class KnowledgeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeCategory
        fields = '__all__'

class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeDocument
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'uploader')
