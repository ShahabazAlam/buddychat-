from django.conf import settings
from django.db import models

from user_accounts.models import User
from django.utils.timezone import now
import datetime


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # who sent the request
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')  # who will receive the request
    #sender = models.CharField(max_length=20, default='requested')
    status = models.CharField(max_length=20, default='requested')
    created_at = models.DateTimeField(default=datetime.datetime.now)


class Block(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block')  # who sent the request
    friend = models.ForeignKey(User, on_delete=models.CASCADE,related_name='block_friend')  # who will receive the request
    #sender = models.CharField(max_length=20, default='requested')
    status = models.CharField(max_length=20, default='block')
    created_at = models.DateTimeField(default=datetime.datetime.now)






