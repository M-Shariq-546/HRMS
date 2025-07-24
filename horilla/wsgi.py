"""
WSGI config for horilla project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from horilla.utils.logger import HorillaLogger

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horilla.settings")

# Configure logging
logger = HorillaLogger("horilla.wsgi")

# Log startup information
logger.info('Horilla application starting up...')
logger.info('Logging mode: %s', os.environ.get('DJANGO_LOGGING_MODE', 'development'))
logger.info('Debug mode: %s', os.environ.get('DEBUG', 'False'))
logger.info('Graylog handler configured and ready')

application = get_wsgi_application()
