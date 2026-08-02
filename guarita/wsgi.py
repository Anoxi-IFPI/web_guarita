"""
WSGI config for guarita project.
...
"""
import os

from django.core.wsgi import get_wsgi_application

# A URL que estava aqui foi removida!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guarita.settings')

application = get_wsgi_application()
app = application