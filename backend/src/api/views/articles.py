from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
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


class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing articles.
    
    Provides standard CRUD operations plus custom 'promoted' action for featured articles.
    Supports search, filtering by category and tags.
    """
    serializer_class = ArticleSerializer
    pagination_class = ArticlePagination

    def get_queryset(self):
        """Return published articles with optional filtering.
        
        Query parameters:
        - search: Full-text search on title/content/category
        - category: Filter by category slug or name
        - tags: Comma-separated list of tag names
        """
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
        """Allow anyone to read, require authentication for create/update/delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @swagger_auto_schema(tags=['Articles'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Articles', 'Admin'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Articles'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Articles', 'Admin'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Articles', 'Admin'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Articles', 'Admin'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    @swagger_auto_schema(tags=['Articles'])
    def promoted(self, request):
        """Get promoted/featured articles.
        
        Query parameters:
        - limit: Number of promoted articles to return (optional)
        """
        qs = Article.objects.filter(is_promoted=True, is_published=True).order_by('-created_at')
        
        # Optional limit parameter to return only top N promoted articles
        limit = request.GET.get('limit')
        if limit:
            try:
                n = int(limit)
                qs = qs[:n]
            except Exception:
                pass
        
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
