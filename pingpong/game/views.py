from django.shortcuts import render, redirect
from .models import Game
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import string

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import threading
import math

import math

class GamePlay:
    def __init__(self):
        self.initialBallSpeedX = 3
        self.initialBallSpeedY = 3
        self.ballSpeedY = self.initialBallSpeedY
        self.ballSpeedX = self.initialBallSpeedX
        self.ballRadius = 10
        self.lastCollision = False
        self.canvasWidth = 800
        self.canvasHeight = 400
        self.paddleWith = 10
        self.paddleHeight = 100
        self.leftPlayer = self.canvasHeight / 2 - self.paddleHeight / 2
        self.rightPlayer = self.canvasHeight / 2 - self.paddleHeight / 2
        self.leftPlayerScore = 0
        self.rightPlayerScore = 0
        self.BallX = self.canvasWidth / 2
        self.BallY = self.canvasHeight / 2
        self.gameOver = False

    def leftPlayerMoveUp(self):
        self.leftPlayer += 15
        if self.leftPlayer + self.paddleHeight > self.canvasHeight:
            self.leftPlayer = self.canvasHeight - self.paddleHeight

    def leftPlayerMoveDown(self):
        self.leftPlayer -= 15
        if self.leftPlayer < 0:
            self.leftPlayer = 0

    def rightPlayerMoveUp(self):
        self.rightPlayer += 15
        if self.rightPlayer + self.paddleHeight > self.canvasHeight:
            self.rightPlayer = self.canvasHeight - self.paddleHeight

    def rightPlayerMoveDown(self):
        self.rightPlayer -= 15
        if self.rightPlayer < 0:
            self.rightPlayer = 0

    def checkCollision(self, paddleC, isLeftPlayer):
        paddlePosX = self.paddleWith if isLeftPlayer else self.canvasWidth - self.paddleWith
        if abs(self.BallX - paddlePosX) < self.ballRadius + self.paddleWith / 2:
            withinPaddle = self.BallY > paddleC and self.BallY < paddleC + self.paddleHeight
            if withinPaddle and not self.lastCollision:

                collisionPoint = self.BallY - (paddleC + self.paddleHeight / 2)
                normalizedPoint = collisionPoint / (self.paddleHeight / 2)
                bounceAngle = normalizedPoint * (math.pi / 4)

                if abs(normalizedPoint) > 1:
                    normalizedPoint = 1 if normalizedPoint > 0 else -1
                    bounceAngle = normalizedPoint * (math.pi / 4)

                self.ballSpeedX = -self.ballSpeedX * 1.1
                self.ballSpeedY = self.ballSpeedX * math.tan(bounceAngle)
                self.lastCollision = True
            else:
                self.lastCollision = False
        else:
            self.lastCollision = False


    def resetBall(self):
        self.BallX = self.canvasWidth / 2
        self.BallY = self.canvasHeight / 2
        #self.ballSpeedX = -self.ballSpeedX
        self.ballSpeedX = self.initialBallSpeedX 
        self.ballSpeedY = self.initialBallSpeedY

    def repeat_function(self):
        self.BallX += self.ballSpeedX
        self.BallY += self.ballSpeedY

        if self.BallY + self.ballRadius > self.canvasHeight or self.BallY - self.ballRadius < 0:
            self.ballSpeedY = -self.ballSpeedY

        self.checkCollision(self.leftPlayer, True)
        self.checkCollision(self.rightPlayer, False)

        if self.BallX - self.ballRadius < 0:
            self.rightPlayerScore += 1
            self.resetBall()

        elif self.BallX + self.ballRadius > self.canvasWidth:
            self.leftPlayerScore += 1
            self.resetBall()

        if self.leftPlayerScore == 5 or self.rightPlayerScore == 5:
            self.gameOver = True

        return {
            'BallX': self.BallX,
            'BallY': self.BallY,
            'leftPlayer': self.leftPlayer,
            'rightPlayer': self.rightPlayer,
            'leftPlayerScore': self.leftPlayerScore,
            'rightPlayerScore': self.rightPlayerScore
        }

class EndGame(APIView):
    def post(self, request):
        roomNumber = request.data.get('roomNumber')
        playerScore = request.data.get('playerScore')
        opponentScore = request.data.get('opponentScore')
        username = request.data.get('username')
        game = Game.objects.filter(roomNumber=roomNumber).first()
        if username == game.username_host:
            if game is None:
                return Response({'Error'}, status=400)
            game.hostScore = playerScore
            game.guestScore = opponentScore
            if playerScore > opponentScore:
                game.winner = game.username_host
            else:
                game.winner = game.username_guest
            game.save()
        return Response({game.winner}, status=200)

class CreateRoom(APIView):
    def post(self, request):
        username_host = request.data.get('username_host')
        roomNumber = request.data.get('roomNumber')
        try:
            game_ = Game.objects.filter(roomNumber=roomNumber).first()
            if game_:
                return Response({'error': 'Turnuva mevcut.'}, status=404)
            game = Game.objects.create(
                username_host=username_host,
                roomNumber=roomNumber,
            )
            game.save()
            print("Oyun odası oluşturuldu: ", roomNumber)
            return Response({'OK'}, status=200)
        except Exception as e:
            print(str(e))
            return Response({'error': 'Oyun oluşmadı.'}, status=400)

class JoinRoom(APIView):
    def post(self, request):
        roomNumber = request.data.get('roomNumber')
        game = Game.objects.filter(roomNumber=roomNumber).first()
        if game is None:
            return Response({'ERROR'}, status=200)
        game.username_guest = request.data.get('username_guest')
        game.save()
        return Response({'OK'}, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

class UserStatsView(APIView):
    def get(self, request, username, format=None):
        recent_games = Game.objects.filter(
            Q(username_host=username) | Q(username_guest=username)
        ).exclude(winner__isnull=True).order_by('-id')[:5]

        # Maç sonuçlarını işlemek
        games_data = []
        for game in recent_games:
            if game.winner == game.username_host:
                loser = game.username_guest
            else:
                loser = game.username_host

            games_data.append({
                'opponent': game.username_guest if game.username_host == username else game.username_host,
                'winner': game.winner,
                'loser': loser,
                'roomNumber': game.roomNumber,  
                'hostScore': game.hostScore,    
                'guestScore': game.guestScore,  
            })

        return Response({
            'username': username,
            'recent_games': games_data
        })
