#chat/rooting

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/status/<str:username>/', consumers.UserConsumer.as_asgi()),
]