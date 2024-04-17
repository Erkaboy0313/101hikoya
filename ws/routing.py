from django.urls import re_path
from .consumer import KitabConsumer

websocket_urlpatterns = [
    re_path(r'ws/default_room/', KitabConsumer.as_asgi()),
]