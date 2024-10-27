from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from .models import Room, Message
#from ../users.model import User, Friend

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        # Odayı oluştur veya getir
        await self.get_or_create_room(self.room_name)

        # Odaya katıl
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Önceki mesajları getir ve gönder
        previous_messages = await self.get_previous_messages(self.room_name)
        for message in previous_messages:
            await self.send(text_data=json.dumps({
                'message': message.content,
                'username': message.username
            }))

    async def disconnect(self, close_code):
        # Odadan ayrıl
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        username = data.get('username')

        if message:
            # Mesajı kaydet ve gruba yayınla
            await self.save_message(username, self.room_name, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username
                }
            )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Mesajı WebSocket'e gönder
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def get_or_create_room(self, room_name):
        Room.objects.get_or_create(name=room_name)

    @sync_to_async
    def save_message(self, username, room_name, message):
        room = Room.objects.get(name=room_name)
        Message.objects.create(username=username, room=room, content=message)

    @sync_to_async
    def get_previous_messages(self, room_name):
        try:
            room = Room.objects.get(name=room_name)
            return list(Message.objects.filter(room=room).order_by('date_added'))
        except Room.DoesNotExist:
            return []