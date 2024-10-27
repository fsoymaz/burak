import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game
from .views import *
import asyncio

class GameRoom:
    def __init__(self, room_name):
        self.room_name = room_name
        self.player_count = 0
        self.game = None

    def add_player(self):
        self.player_count += 1
        return self.player_count

    def remove_player(self):
        self.player_count -= 1
        if self.player_count <= 0:
            return True
        return False


class GameRoomConsumer:
    rooms = {}
    tournament = False

    @classmethod
    def get_or_create_room(cls, room_name):
        if room_name not in cls.rooms:
            cls.rooms[room_name] = GameRoom(room_name)
        return cls.rooms[room_name]

    @classmethod
    def remove_room(cls, room_name):
        if room_name in cls.rooms:
            del cls.rooms[room_name]


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        self.room = GameRoomConsumer.get_or_create_room(self.room_name)

        player_count = self.room.add_player()
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        if player_count == 2:
            # İkinci oyuncu geldi, oyunu başlat
            self.room.game = GamePlay()  # Doğrudan bir GamePlay nesnesi oluşturun
            await self.start_game()

    async def disconnect(self, close_code):
        # Odadan oyuncu çıkar ve eğer oda boşsa odayı sil
        if self.room.remove_player():
            GameRoomConsumer.remove_room(self.room_name)

        # Grubu bırak
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if hasattr(self, 'game_loop_task'):
            self.game_loop_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data == 1:
            self.room.game.leftPlayerMoveUp()
        elif data == 2:
            self.room.game.leftPlayerMoveDown()
        elif data == 3:
            self.room.game.rightPlayerMoveUp()
        elif data == 4:
            self.room.game.rightPlayerMoveDown()

    async def game(self, event):
        action = self.room.game.repeat_function()
        await self.send(text_data=json.dumps(action))

    async def game_loop(self):
        while (self.room.game.gameOver is False) or (self.leftPlayerScore < 6 or self.rightPlayerScore < 6):
            await asyncio.sleep(0.03)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game',
                })

    async def start_game(self):
        self.game_loop_task = asyncio.create_task(self.game_loop())