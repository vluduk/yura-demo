from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.business import BusinessIdeaViewSet

router = DefaultRouter()
router.register(r'business-ideas', BusinessIdeaViewSet, basename='business-idea')

urlpatterns = [
    path('', include(router.urls)),
]
