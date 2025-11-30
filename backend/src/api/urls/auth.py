from django.urls import path
from api.views.auth import SignUpView, LoginView, LogoutView, RefreshView, MeView, CreateAdminView

urlpatterns = [
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('refresh', RefreshView.as_view(), name='refresh'),
    path('me', MeView.as_view(), name='me'),
    path('create-admin', CreateAdminView.as_view(), name='create-admin'),
]
