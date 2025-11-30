from rest_framework import serializers
from api.models.knowledge import KnowledgeCategory, KnowledgeDocument


class KnowledgeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeCategory
        fields = ('id', 'name')
        read_only_fields = ('id',)


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    category = KnowledgeCategorySerializer(read_only=True)
    uploader = serializers.PrimaryKeyRelatedField(read_only=True)
    embedding = serializers.ReadOnlyField()

    class Meta:
        model = KnowledgeDocument
        fields = (
            'id', 'uploader', 'category', 'title', 'raw_text_content', 'source_url',
            'embedding', 'created_at'
        )
        read_only_fields = ('id', 'embedding', 'created_at')
