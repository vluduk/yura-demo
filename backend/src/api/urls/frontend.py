from django.urls import re_path
from django.views.generic import TemplateView

# Serve the compiled Angular index.html as the root. TemplateView will
# look for `index.html` in the configured template dirs / static files.
urlpatterns = [
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='frontend'),
]
