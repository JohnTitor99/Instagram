"""
ASGI config for instagram project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.direct.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket': AuthMiddlewareStack( # list of protocols and use AuthMiddlewareStack to wrap the url router
        URLRouter(
            apps.direct.routing.websocket_urlpatterns # url patterns list from routing.py
        )
    )
})