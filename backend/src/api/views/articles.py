from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from django.conf import settings

from api.models.article import Article
from api.serializers.article import ArticleSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

try:
    # Postgres full-text search
    from django.contrib.postgres.search import SearchVector, SearchQuery
except Exception:
    SearchVector = None
    SearchQuery = None


class ArticlePagination(PageNumberPagination):
    page_size = getattr(settings, 'DEFAULT_PAGE_SIZE', 20)
    page_size_query_param = 'limit'
    max_page_size = 100


class ArticleListCreateView(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination

    def get_queryset(self):
        # Only return published articles by default
        qs = Article.objects.filter(is_published=True).order_by('-created_at')

        # Search: try to use Postgres full-text search when available, otherwise fallback to icontains
        search = self.request.GET.get('search')
        if search:
            if SearchVector and SearchQuery:
                try:
                    sv = SearchVector('title', 'content')
                    sq = SearchQuery(search)
                    qs = qs.annotate(search=sv).filter(search=sq)
                except Exception:
                    from django.db.models import Q

                    qs = qs.filter(
                        Q(title__icontains=search) | Q(content__icontains=search) | Q(category__name__icontains=search)
                    )
            else:
                from django.db.models import Q

                qs = qs.filter(
                    Q(title__icontains=search) | Q(content__icontains=search) | Q(category__name__icontains=search)
                )

        # Filter by category (accept slug or exact name)
        category = self.request.GET.get('category')
        if category:
            from django.db.models import Q

            qs = qs.filter(Q(category__slug=category) | Q(category__name__iexact=category))

        # Filter by tags (comma-separated list of tag names)
        tags = self.request.GET.get('tags')
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if tag_list:
                qs = qs.filter(tags__name__in=tag_list).distinct()

        return qs

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
        qs = Article.objects.filter(is_promoted=True, is_published=True).order_by('-created_at')
        # Optional limit parameter to return only top N promoted articles
        limit = self.request.GET.get('limit')
        if limit:
            try:
                n = int(limit)
                return qs[:n]
            except Exception:
                pass
        return qs


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]  # Allow reading by anyone, but update/delete might need restriction

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
