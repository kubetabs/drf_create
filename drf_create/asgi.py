"""
ASGI config for drf_create project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from .websocket import log_consumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_create.settings')

django_application = get_asgi_application()


async def application(scope, receive, send):
    if scope['type'] == 'http':
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await log_consumer(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")
