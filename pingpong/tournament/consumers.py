import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from .views import *
from .models import Tournament
from asgiref.sync import sync_to_async

# GameRoom sınıfı, her oyun odasını ve oyuncularını yönetir
class GameRoom:
    def __init__(self, room_name):
        self.room_name = room_name
        self.game_group1 = None
        self.game_group2 = None
        self.players = []
        self.start_game = False
        self.start_game_final = False
        self.lock = asyncio.Lock()

    def add_player(self, player_name):
        if player_name not in self.players:
            self.players.append(player_name)
        return len(self.players)

    def remove_player(self, player_name):
        if player_name in self.players:
            self.players.remove(player_name)
        return len(self.players)

# WebSocket bağlantılarını ve oyun mantığını yöneten tüketici sınıfı
class TournamentConsumer(AsyncWebsocketConsumer):
    rooms = {}  # Tüm oyun odalarını takip etmek için bir sözlük

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    @classmethod
    def get_or_create_room(cls, room_name):
        if room_name not in cls.rooms:
            cls.rooms[room_name] = GameRoom(room_name)
        return cls.rooms[room_name]

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        self.room = self.get_or_create_room(self.room_name)

        # Oyun odasına bağlan
        if not self.room_name[-1] == 'f':
            if len(self.room.players) % 2 == 0:
                await self.channel_layer.group_add(
                    self.room_group_name + "_1",
                    self.channel_name
                )
            else:
                await self.channel_layer.group_add(
                    self.room_group_name + "_2",
                    self.channel_name
                )
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if self.room.start_game:
            await self.handle_game_actions(data)
        elif self.room.start_game_final:
            await self.final_handle_game_actions(data)
        elif 'name' in data:
            player_name = data['name']
            if player_name not in self.room.players:
                self.room.add_player(player_name)
                await self.send_message()
        elif 'start_game' in data:
            self.room.start_game = True
            await asyncio.sleep(1)
            await self.start_group_games()
        elif 'start_game_f' in data and len(self.room.players) == 2:  # Hata düzeltildi
            self.room.start_game_final = True
            await asyncio.sleep(1)
            await self.start_final_games()

    async def handle_game_actions(self, data):
        if 'name' in data:
            player_index = self.room.players.index(data['name'])
            message = data['message']

            # Oyuncu hareketlerini yönet
            if player_index == 0 and message == 2:
                self.room.game_group1.leftPlayerMoveUp()
            elif player_index == 0 and message == 1:
                self.room.game_group1.leftPlayerMoveDown()
            elif player_index == 2 and message == 2:
                self.room.game_group1.rightPlayerMoveUp()
            elif player_index == 2 and message == 1:
                self.room.game_group1.rightPlayerMoveDown()
            elif player_index == 1 and message == 2:
                self.room.game_group2.leftPlayerMoveUp()
            elif player_index == 1 and message == 1:
                self.room.game_group2.leftPlayerMoveDown()
            elif player_index == 3 and message == 2:
                self.room.game_group2.rightPlayerMoveUp()
            elif player_index == 3 and message == 1:
                self.room.game_group2.rightPlayerMoveDown()

    async def final_handle_game_actions(self, data):
        if 'name' in data:
            player_index = self.room.players.index(data['name'])
            message = data['message']

            if player_index == 0 and message == 2:
                self.room.final.leftPlayerMoveUp()
            elif player_index == 0 and message == 1:
                self.room.final.leftPlayerMoveDown()
            elif player_index == 1 and message == 2:
                self.room.final.rightPlayerMoveUp()
            elif player_index == 1 and message == 1:
                self.room.final.rightPlayerMoveDown()

    async def send_message(self):
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'tournament_message',
                    'players': self.room.players,
                }
            )
        except Exception as e:
            print(f"Error in group send: {e}")

    async def tournament_message(self, event):
        players = event['players']
        try:
            await self.send(text_data=json.dumps({'players': players}))
            await self.send(text_data=json.dumps({'room_name': self.room_name}))
        except Exception as e:
            print(f"Error sending message: {e}") # 'players' anahtarı değiştirildi

    async def start_final_games(self):
        await asyncio.sleep(0.03)
        self.room.final = GamePlay()  # GamePlay tanımlı olduğundan emin olun

        self.game_final = asyncio.create_task(self.start_game_final(self.room.final, self.room_group_name))

    async def start_game_final(self, game, group_name):
        while not game.gameOver:
            await asyncio.sleep(0.03)  # Simüle edilen oyun turları
            game_state = game.repeat_function()
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'game_update',
                    'game': game_state,
                }
            )

        tournament = await sync_to_async(Tournament.objects.filter(roomNumber=self.room_name[:-1]).first)()  # 'tournament' nesnesi düzeltildi

        if game == self.room.final:
            # Kazananı belirleme
            if tournament.user1Score > tournament.user3Score:
                tournament.finalUser1 = tournament.user1
            else:
                tournament.finalUser1 = tournament.user3

            if tournament.user2Score > tournament.user4Score:
                tournament.finalUser2 = tournament.user2
            else:
                tournament.finalUser2 = tournament.user4

            tournament.finalUser1Score = game.leftPlayerScore
            tournament.finalUser2Score = game.rightPlayerScore

            if game.leftPlayerScore > game.rightPlayerScore:
                tournament.winner = tournament.finalUser1
            else:
                tournament.winner = tournament.finalUser2

            await sync_to_async(tournament.save)()

    async def start_group_games(self):
        await asyncio.sleep(0.03)  # Oyun başlaması için kısa bir bekleme

        # Oyuncuları iki gruba ayır
        self.group1 = [self.room.players[0], self.room.players[2]]
        self.group2 = [self.room.players[1], self.room.players[3]]

        # Her grup için oyunları başlat
        self.room.game_group1 = GamePlay()
        self.room.game_group2 = GamePlay()

        self.game_loop_task1 = asyncio.create_task(self.start_game(self.room.game_group1, self.room_group_name + "_1"))
        self.game_loop_task2 = asyncio.create_task(self.start_game(self.room.game_group2, self.room_group_name + "_2"))

    async def start_game(self, game, group_name):
        # Eşzamanlı veri erişimini kontrol etmek için kilit oluşturuyoruz

        # Oyun devam ederken oyun durumu güncellemelerini gönderiyoruz
        while not game.gameOver:
            await asyncio.sleep(0.03)  # Simüle edilen oyun turları
            game_state = game.repeat_function()
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'game_update',
                    'game': game_state,
                }
            )

        async with self.room.lock:
            try:
                print("hello world")
                # Turnuva kaydını alın
                tournament = await sync_to_async(Tournament.objects.filter(roomNumber=self.room_name).first)()
                if not tournament:
                    print("Tournament not found.")
                    return

                # Skorları güncelleyin
                if game == self.room.game_group1:
                    tournament.user1Score = game.leftPlayerScore
                    tournament.user3Score = game.rightPlayerScore
                    print(
                        f"Group 1 - Left Player Score: {game.leftPlayerScore}, Right Player Score: {game.rightPlayerScore}")

                elif game == self.room.game_group2:
                    tournament.user2Score = game.leftPlayerScore
                    tournament.user4Score = game.rightPlayerScore
                    print(
                        f"Group 2 - Left Player Score: {game.leftPlayerScore}, Right Player Score: {game.rightPlayerScore}")

                # Veritabanı güncellemelerini kaydedin
                await sync_to_async(tournament.save)()
                print("Scores saved to the database.")

            except Exception as e:
                print(f"An error occurred while updating scores: {e}")


    async def disconnect(self, close_code):
        try:
            # Remove the user from group 1
            await self.channel_layer.group_discard(
                self.room_group_name + "_1",
                self.channel_name
            )

            # Remove the user from group 2
            await self.channel_layer.group_discard(
                self.room_group_name + "_2",
                self.channel_name
            )

            # Remove the user from the general group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            # Remove the player's name from the game room
            if self.scope['user'].username in self.room.players:
                self.room.remove_player(self.scope['user'].username)

            # Send the updated player list to all clients
            await self.send_message()

        except Exception as e:
            print(f"Error during disconnect: {e}")

    async def game_update(self, event):
        game_data = event['game']

        # Tüm istemcilere oyun durumunu gönder
        await self.send(text_data=json.dumps({
            'BallX': game_data['BallX'],
            'BallY': game_data['BallY'],
            'leftPlayer': game_data['leftPlayer'],
            'rightPlayer': game_data['rightPlayer'],
            'leftPlayerScore': game_data['leftPlayerScore'],
            'rightPlayerScore': game_data['rightPlayerScore'],
        }))
