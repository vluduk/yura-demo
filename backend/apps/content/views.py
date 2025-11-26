from rest_framework import generics, permissions, filters
from .models import Article, ArticleCategory
from .serializers import ArticleSerializer, ArticleCategorySerializer

class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'id'
    lookup_url_kwarg = 'article_id'

class PromotedArticleListView(generics.ListAPIView):
    queryset = Article.objects.filter(is_promoted=True, is_published=True)
    serializer_class = ArticleSerializer
    permission_classes = (permissions.AllowAny,)

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'id'
    lookup_url_kwarg = 'filter_id'
