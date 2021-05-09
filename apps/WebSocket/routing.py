from django.urls import re_path

from .chat_consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"^chat/(?P<username>[\w.@+-]+)/$", ChatConsumer.as_asgi()),
]
