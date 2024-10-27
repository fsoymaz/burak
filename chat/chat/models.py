from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=255)

class Message(models.Model):
    username = models.CharField(max_length=255)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)