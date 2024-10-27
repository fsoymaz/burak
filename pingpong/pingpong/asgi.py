import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import game.routing
import tournament.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pingpong.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            game.routing.websocket_urlpatterns + tournament.routing.websocket_urlpatterns
        )
    ),
})
