from django.db import models

# Create your models here.
class Tournament(models.Model):
    user1 = models.CharField(max_length=100, null=True, blank=True)
    user2 = models.CharField(max_length=100, null=True, blank=True)
    user3 = models.CharField(max_length=100, null=True, blank=True)
    user4 = models.CharField(max_length=100, null=True, blank=True)
    finalUser1 = models.CharField(max_length=100, null=True, blank=True)
    finalUser2 = models.CharField(max_length=100, null=True, blank=True)
    user4 = models.CharField(max_length=100, null=True, blank=True)
    user1Score = models.IntegerField(default=0)
    user2Score = models.IntegerField(default=0)
    user3Score = models.IntegerField(default=0)
    user4Score = models.IntegerField(default=0)
    finalUser1Score = models.IntegerField(default=0)
    finalUser2Score = models.IntegerField(default=0)
    roomNumber = models.IntegerField(default=0)
    winner = models.CharField(max_length=100, null=True, blank=True)










# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio
# from .views import *
# from .models import Tournament

# # GameRoom sınıfı, her oyun odasını ve oyuncularını yönetir
# class GameRoom:
#     def __init__(self, room_name):
#         self.room_name = room_name
#         self.game_group1 = None
#         self.game_group2 = None
#         self.players = []  # Oyuncu isimlerini depolamak için bir liste
#         self.start_game = False
#         self.group1_winner = None  # Grup 1 kazananı
#         self.group2_winner = None  # Grup 2 kazananı

#     def add_player(self, player_name):
#         if player_name not in self.players:
#             self.players.append(player_name)
#         return len(self.players)

#     def remove_player(self, player_name):
#         if player_name in self.players:
#             self.players.remove(player_name)
#         return len(self.players)

# # WebSocket bağlantılarını ve oyun mantığını yöneten tüketici sınıfı
# class TournamentConsumer(AsyncWebsocketConsumer):
#     rooms = {}  # Tüm oyun odalarını takip etmek için bir sözlük

#     @classmethod
#     def get_or_create_room(cls, room_name):
#         if room_name not in cls.rooms:
#             cls.rooms[room_name] = GameRoom(room_name)
#         return cls.rooms[room_name]

#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'game_{self.room_name}'

#         # Oyun odasını al veya oluştur
#         self.room = self.get_or_create_room(self.room_name)

#         print("oyun = " + self.room_name)

#         # Oyun gruplarını oyuncu sayısına göre ayarla
#         if len(self.room.players) % 2 == 0:
#             await self.channel_layer.group_add(
#                 self.room_group_name + "_1",
#                 self.channel_name
#             )
#         else:
#             await self.channel_layer.group_add(
#                 self.room_group_name + "_2",
#                 self.channel_name
#             )

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()  # WebSocket bağlantısını kabul et

#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         if self.room.start_game:
#             await self.handle_game_actions(data)
#         elif 'name' in data:
#             player_name = data['name']
#             if player_name not in self.room.players:
#                 self.room.add_player(player_name)
#                 await self.send_message()
#         elif 'start_game' in data:
#             self.room.start_game = True
#             await asyncio.sleep(1)
#             await self.send(text_data=json.dumps({'players': 123}))
#             await self.start_group_games()

#     async def handle_game_actions(self, data):
#         player_index = self.room.players.index(data['name'])
#         message = data['message']
        
#         if player_index == 0 and message == 2:
#             self.room.game_group1.leftPlayerMoveUp()
#         elif player_index == 0 and message == 1:
#             self.room.game_group1.leftPlayerMoveDown()
#         elif player_index == 2 and message == 2:
#             self.room.game_group1.rightPlayerMoveUp()
#         elif player_index == 2 and message == 1:
#             self.room.game_group1.rightPlayerMoveDown()
#         elif player_index == 1 and message == 2:
#             self.room.game_group2.leftPlayerMoveUp()
#         elif player_index == 1 and message == 1:
#             self.room.game_group2.leftPlayerMoveDown()
#         elif player_index == 3 and message == 2:
#             self.room.game_group2.rightPlayerMoveUp()
#         elif player_index == 3 and message == 1:
#             self.room.game_group2.rightPlayerMoveDown()

#     async def send_message(self):
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'tournament_message',
#                 'players': self.room.players,
#             }
#         )

#     async def tournament_message(self, event):
#         players = event['players']
#         await self.send(text_data=json.dumps({'players': players}))
#         await self.send(text_data=json.dumps({'players': self.room_name}))

#     async def start_group_games(self):
#         await asyncio.sleep(0.03)  # Oyun başlaması için kısa bir bekleme

#         # Oyuncuları iki gruba ayır
#         self.group1 = [self.room.players[0], self.room.players[2]]
#         self.group2 = [self.room.players[1], self.room.players[3]]

#         # Her grup için oyunları başlat
#         self.room.game_group1 = GamePlay()
#         self.room.game_group2 = GamePlay()

#         self.game_loop_task1 = asyncio.create_task(self.start_game(self.room.game_group1, self.room_group_name + "_1"))
#         self.game_loop_task2 = asyncio.create_task(self.start_game(self.room.game_group2, self.room_group_name + "_2"))
#         while(not self.room.group1_winner or not self.room.group2_winner):
#             await asyncio.sleep(1)
#         if self.room.group1_winner and self.room.group2_winner:
#             await self.start_final_game()

#     async def start_game(self, game, group_name):
#         while not game.gameOver:
#             await asyncio.sleep(0.03)  # Simüle edilen oyun turları
#             game_state = game.repeat_function()
#             await self.channel_layer.group_send(
#                 group_name,
#                 {
#                     'type': 'game_update',
#                     'game': game_state,
#                 }
#             )
        
#         self.room.game_final = GamePlay()
#         self.final_group_name = f'{self.room_group_name}_final'

#         # Kazananları belirleyin ve gruptan çıkarın
#         tournament = tournament.objects.get(roomNumber=self.room_name)

#         if game == self.room.game_group1:
#             tournament.user1Score = game.leftPlayerScore
#             tournament.user3Score = game.rightPlayerScore
#             tournament.save()
#             if game.leftPlayerScore > game.rightPlayerScore:
#                 await self.channel_layer.group_add(self.final_group_name, self.channel_name)
#                 self.room.group1_winner = self.group1[0]
#                 tournament.user1 =
#             else:
#                 await self.channel_layer.group_add(self.final_group_name, self.channel_name)
#                 self.room.group1_winner = self.group1[1]
#         elif game == self.room.game_group2:
#             tournament.user2Score = game.leftPlayerScore
#             tournament.user4Score = game.rightPlayerScore
#             tournament.save()
#             if game.leftPlayerScore > game.rightPlayerScore:
#                 await self.channel_layer.group_add(self.final_group_name, self.channel_name)
#                 self.room.group2_winner = self.group2[0]
#             else:
#                 await self.channel_layer.group_add(self.final_group_name, self.channel_name)
#                 self.room.group2_winner = self.group2[1]

#         # İki kazanan belirlenirse final oyununu başlat


#     async def start_final_game(self):
#         # Kazananları final oyununa katılmak için eşleştirin
#         # final_players = [self.room.group1_winner, self.room.group2_winner]

#         # # Yeni bir oyun başlat
#         # self.room.game_final = GamePlay()
#         # self.final_group_name = f'{self.room_group_name}_final'

#         # # Final grubu için yeni oyun başlat
#         # await self.channel_layer.group_add(self.final_group_name, self.channel_name)

#         # Final oyunu için oyun döngüsü başlat
#         asyncio.create_task(self.start_game(self.room.game_final, self.final_group_name))

#     async def disconnect(self, close_code):
#         # Kullanıcıyı grup 1'den çıkar
#         await self.channel_layer.group_discard(
#             self.room_group_name + "_1",  # Grup 1 adı
#             self.channel_name  # Kullanıcının kanal adı
#         )

#         # Kullanıcıyı grup 2'den çıkar
#         await self.channel_layer.group_discard(
#             self.room_group_name + "_2",  # Grup 2 adı
#             self.channel_name
#         )

#         # Genel gruptan da çıkar
#         await self.channel_layer.group_discard(
#             self.room_group_name,  # Genel grup adı
#             self.channel_name
#         )

#         # Oyun odasından kullanıcının adını kaldır
#         if self.scope['user'].username in self.room.players:
#             self.room.remove_player(self.scope['user'].username)

#         # Tüm istemcilere güncellenmiş oyuncu listesini gönder
#         await self.send_message()

#     async def game_update(self, event):
#         game_data = event['game']

#         # Tüm istemcilere oyun durumunu gönder
#         await self.send(text_data=json.dumps({
#             'BallX': game_data['BallX'],
#             'BallY': game_data['BallY'],
#             'leftPlayer': game_data['leftPlayer'],
#             'rightPlayer': game_data['rightPlayer'],
#             'leftPlayerScore': game_data['leftPlayerScore'],
#             'rightPlayerScore': game_data['rightPlayerScore'],
#         }))
