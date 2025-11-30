from rest_framework import generics, permissions
from api.models.article import Article
from api.serializers.article import ArticleSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @swagger_auto_schema(tags=['Articles'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Articles', 'Admin'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PromotedArticlesView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(is_promoted=True, is_published=True).order_by('-created_at')
