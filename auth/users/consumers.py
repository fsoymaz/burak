from channels.generic.websocket import AsyncWebsocketConsumer
import json

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'user_{self.room_name}'

        # Check if channel_layer is correctly initialized
        if self.channel_layer is None:
            await self.close()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        #await self.channel_layer.group_send(
        #    self.room_group_name,
        #    {
        #        'type': 'chat_message',
        #        'message': 0
        #    }
        #)
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_message',
                'message': message
            }
        )

    async def user_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
