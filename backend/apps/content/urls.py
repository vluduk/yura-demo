from django.urls import path
from .views import ArticleListCreateView, ArticleDetailView, PromotedArticleListView, CategoryListCreateView, CategoryDetailView

urlpatterns = [
    path('', ArticleListCreateView.as_view(), name='article-list'),
    path('promoted', PromotedArticleListView.as_view(), name='article-promoted'),
    path('<uuid:article_id>', ArticleDetailView.as_view(), name='article-detail'),
    
    # Filters (Categories)
    path('filters', CategoryListCreateView.as_view(), name='category-list'),
    path('filters/<uuid:filter_id>', CategoryDetailView.as_view(), name='category-detail'),
]
