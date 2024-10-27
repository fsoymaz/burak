from django.urls import path
from . import views
from .views import CreateRoom, JoinRoom, EndGame

urlpatterns = [
    # path('', views.index, name='index'),
    path('create_room/', CreateRoom.as_view(), name='create_room'),
    path('join_room/', JoinRoom.as_view(), name='join_room'),
    path('end_game/', EndGame.as_view(), name='join_room'),

    # path('game/<str:room_name>/', views.game_view, name='game'),
]
