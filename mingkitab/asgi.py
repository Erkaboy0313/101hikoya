"""
ASGI config for mingkitab project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mingkitab.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from .customauth import TokenAuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application


django_asgi_app = get_asgi_application()

from ws.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket":AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                    websocket_urlpatterns
                )
            ),
        ),
    })

