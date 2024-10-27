from django.db import models

class Game(models.Model):
    username_host = models.CharField(max_length=100, null=True, blank=True)
    username_guest = models.CharField(max_length=100, null=True, blank=True)
    hostScore = models.IntegerField(default=0)
    guestScore = models.IntegerField(default=0)
    roomNumber = models.CharField(max_length=100)
    winner = models.CharField(max_length=100, null=True, blank=True)

