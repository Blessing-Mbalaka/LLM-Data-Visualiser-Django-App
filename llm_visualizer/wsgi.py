"""
WSGI config for llm_visualizer project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_visualizer.settings')

application = get_wsgi_application()
