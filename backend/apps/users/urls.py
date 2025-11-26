from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignUpView, LoginView, LogoutView, CreateAdminView

urlpatterns = [
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('create-admin', CreateAdminView.as_view(), name='create-admin'),
]
