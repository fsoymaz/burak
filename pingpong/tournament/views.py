from time import sleep

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Tournament
import math

class GamePlay:
    def __init__(self):
        self.ballSpeedY = 5
        self.ballSpeedX = 5
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
        if abs(self.BallX - paddlePosX) < self.ballRadius + self.paddleWith:
            withinPaddle = self.BallY > paddleC and self.BallY < paddleC + self.paddleHeight
            if withinPaddle and not self.lastCollision:

                collisionPoint = self.BallY - (paddleC + self.paddleHeight / 2)
                normalizedPoint = collisionPoint / (self.paddleHeight / 2)
                bounceAngle = normalizedPoint * (math.pi / 4)

                self.ballSpeedX = -self.ballSpeedX * 1.1
                self.ballSpeedY = self.ballSpeedX * math.tan(bounceAngle)
                self.lastCollision = True
        else:
            self.lastCollision = False

    def resetBall(self):
        self.BallX = self.canvasWidth / 2
        self.BallY = self.canvasHeight / 2
        self.ballSpeedX = -self.ballSpeedX

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

class CreateRoom(APIView):
    def post(self, request):
        username = request.data.get('username')
        roomNumber = request.data.get('roomNumber')
        try:
            tournament_ = Tournament.objects.filter(roomNumber=roomNumber).first()
            if tournament_:
                return Response({'error': 'Turnuva mevcut.'}, status=404)
            tournament = Tournament.objects.create(
                user1=username,
                roomNumber=roomNumber,
            )
            tournament.save()
            print("Oyun odası oluşturuldu: ", roomNumber)
            return Response({'OK'}, status=200)
        except Exception as e:
            print(str(e))
            return Response({'error': 'Oyun oluşmadı.'}, status=400)

def add_player(tournament, username):
    if tournament.user2 is None:
        tournament.user2 = username
    elif tournament.user3 is None:
        tournament.user3 = username
    elif tournament.user4 is None:
        tournament.user4 = username
    else:
        print("Room is full")
    tournament.save()


class CreateRoom(APIView):
    def post(self, request):
        username = request.data.get('username')
        roomNumber = request.data.get('roomNumber')
        try:
            tournament = Tournament.objects.create(
                user1=username,
                roomNumber=roomNumber,
            )
            tournament.save()
            print("Oyun odası oluşturuldu: ", roomNumber)

        except Exception as e:
            print(str(e))
            return Response({'error': 'Oyun oluşmadı.'}, status=400)
        return Response({'OK'}, status=200)

class JoinRoom(APIView):
    def post(self, request):
        username = request.data.get('username')
        roomNumber = request.data.get('roomNumber')
        try:
            tournament = Tournament.objects.filter(roomNumber=roomNumber).first()
            add_player(tournament, username)
            print("Oyuncu eklendi: ", username)
            return Response({'OK'}, status=200)
        except Exception as e:
            print(str(e))
            return Response({'error': 'Oyuncu eklenemedi.'}, status=400)

from rest_framework.response import Response
from rest_framework.views import APIView

class EndGame(APIView):
    def post(self, request):
        sleep(3)
        roomNumber = request.data.get('roomNumber')
        username = request.data.get('username')
        try:
            tournament = Tournament.objects.filter(roomNumber=roomNumber).first()
            if not tournament:
                return Response({'error': 'Turnuva bulunamadı.'}, status=404)
            if tournament.finalUser1 == username:
                if tournament.finalUser1Score > tournament.finalUser2Score:
                    return Response({'result': 'f_winner'}, status=200)
                else:
                    return Response({'result': 'loser'}, status=200)
            elif tournament.finalUser2 == username:
                if tournament.finalUser2Score > tournament.finalUser1Score:
                    return Response({'result': 'f_winner'}, status=200)
                else:
                    return Response({'result': 'loser'}, status=200)
            elif tournament.user1 == username:
                if tournament.user1Score > tournament.user3Score:
                    return Response({'result': 'winner'}, status=200)
                else:
                    return Response({'result': 'loser'}, status=200)
            elif tournament.user2 == username:
                if tournament.user2Score > tournament.user4Score:
                    return Response({'result': 'winner'}, status=200)
                else:
                    return Response({'result': 'loser'}, status=200)
            elif tournament.user3 == username:
                if tournament.user3Score > tournament.user1Score:
                    return Response({'result': 'winner'}, status=200)
                else:
                    return Response({'result': 'loser'}, status=200)
            elif tournament.user4 == username:
                if tournament.user4Score > tournament.user2Score:
                    return Response({'result': 'winner'}, status=200)
                else:
                    return Response({'result': 'loser'}, status=200)
            
            else:
                return Response({'error': 'Oyun sonlandırılamadı.'}, status=400)
        except Exception as e:
            print(str(e))
            return Response({'error': 'Oyun sonlandırılamadı.'}, status=400)
