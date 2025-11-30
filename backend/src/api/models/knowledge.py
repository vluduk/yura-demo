from django.db import models
from django.conf import settings
import uuid


class KnowledgeCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'knowledge_categories'

    def __str__(self):
        return self.name


class KnowledgeDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='knowledge_documents')
    category = models.ForeignKey(KnowledgeCategory, on_delete=models.SET_NULL, null=True, related_name='documents')
    title = models.CharField(max_length=500)
    raw_text_content = models.TextField()
    source_url = models.CharField(max_length=1000, blank=True, null=True)
    embedding = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'knowledge_documents'

    def __str__(self):
        return self.title
