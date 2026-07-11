"""WSGI config for smart_code_reviewer project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_code_reviewer.settings")

application = get_wsgi_application()
