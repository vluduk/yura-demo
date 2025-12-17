
from .auth import urlpatterns as auth_urlpatterns
from .articles import urlpatterns as articles_urlpatterns
from .conversation import urlpatterns as conversation_urlpatterns
from .resume import urlpatterns as resume_urlpatterns
from .business import urlpatterns as business_urlpatterns
from .file import urlpatterns as file_urlpatterns
from .settings import urlpatterns as settings_urlpatterns

urlpatterns = (
    auth_urlpatterns + 
    articles_urlpatterns + 
    conversation_urlpatterns + 
    resume_urlpatterns + 
    business_urlpatterns + 
    file_urlpatterns +
    settings_urlpatterns
)

__all__ = ['urlpatterns']
