import uuid

from django.contrib.auth import get_user_model
from django.db import models
import datetime
from django.conf import settings
User = get_user_model()


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, related_name='author_room', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_room', on_delete=models.CASCADE)
    author_status = models.CharField(max_length=20,default="disconnected")
    friend_status = models.CharField(max_length=20,default="disconnected")

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_messages', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.DO_NOTHING)
    message = models.TextField()
    delete_user = models.TextField(null=True,blank=True,default=None)
    status = models.CharField(max_length=20,default="not deleted")
    read_status = models.CharField(max_length=20,default="pending")
    timestamp = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.message + " " + str(self.timestamp)



