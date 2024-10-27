from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/tournament/<str:room_name>/', consumers.TournamentConsumer.as_asgi()),
]
