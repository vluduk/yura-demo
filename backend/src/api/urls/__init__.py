from .auth import urlpatterns as auth_urlpatterns
from .articles import urlpatterns as articles_urlpatterns

urlpatterns = auth_urlpatterns + articles_urlpatterns

__all__ = ['urlpatterns']
