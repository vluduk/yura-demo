from django.urls import path
from api.views.health import HealthCheckView

urlpatterns = [
    path('', HealthCheckView.as_view(), name='health'),
]
