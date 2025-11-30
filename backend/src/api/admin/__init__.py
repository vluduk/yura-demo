"""Admin package for the `api` app.

Import submodules so Django's admin autodiscovery picks up registrations
when it imports `api.admin`.
"""

from .user import *
from .registry import *

# Unregister Django's Group model so Groups do not appear in the admin.
from django.contrib.auth.models import Group
from django.contrib import admin as _admin
try:
	_admin.site.unregister(Group)
except Exception:
	# If it's not registered or unregister fails, ignore silently.
	pass
