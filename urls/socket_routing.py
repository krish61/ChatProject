from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from middlewares import TokenAuthMiddleware
from django.urls import path
from apps.WebSocket import chat_consumers

application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddleware(
                URLRouter(
                    [
                        path(
                            "chat/<str:user_to_chat_id>/",
                            chat_consumers.ChatConsumer.as_asgi(),
                        ),
                        path(
                            "json/<str:user_to_chat_id>/",
                            chat_consumers.JsonChatConsumer.as_asgi(),
                        ),
                    ]
                )
            )
        )
    }
)
