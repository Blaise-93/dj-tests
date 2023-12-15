import chats.routing
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from decouple import config
from channels.auth import AuthMiddlewareStack
import os
from dotenv import load_dotenv
load_dotenv()


os.environ.setdefault(('DJANGO_SETTINGS_MODULE'),'pharmaceuticals.settings')

# application = get_asgi_application()

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # We will add WebSocket protocol later. For now, it's just HTTP.
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(chats.routing.websocket_urlpatterns))
        )

    }
)
