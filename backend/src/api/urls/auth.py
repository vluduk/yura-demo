from django.urls import path
from api.views.auth import SignUpView, LoginView, LogoutView, RefreshView, CreateAdminView

urlpatterns = [
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('refresh', RefreshView.as_view(), name='refresh'),
    path('create-admin', CreateAdminView.as_view(), name='create-admin'),
]
