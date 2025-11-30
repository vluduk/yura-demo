
from .auth import urlpatterns as auth_urlpatterns
from .articles import urlpatterns as articles_urlpatterns
from .conversation import urlpatterns as conversation_urlpatterns

urlpatterns = auth_urlpatterns + articles_urlpatterns + conversation_urlpatterns

__all__ = ['urlpatterns']
