from django.urls import path
from api.views.articles import ArticleListCreateView, PromotedArticlesView

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='article-list-create'),
    path('articles/promoted/', PromotedArticlesView.as_view(), name='promoted-articles'),
]
