from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.articles import ArticleViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('', include(router.urls)),
]
