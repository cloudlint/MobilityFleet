#!/usr/bin/env python
"""
WSGI config for scooterrentals project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scooterrentals.settings')

application = get_wsgi_application()
app = application