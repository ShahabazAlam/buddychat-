from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

class User(AbstractUser):
    username = models.EmailField(unique=True,blank=False)
    email = models.EmailField(unique=True, blank=False,
                              error_messages={
                                  'unique': "A user with that email already exists.",
                              })
    gender = models.CharField(max_length=20)
    status = models.BooleanField(default=False)
    about = models.TextField(blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name","last_name", "gender"]
    coverImage = models.TextField(null=True,blank=True)
    profileImage = models.TextField(null=True,blank=True)

    def __unicode__(self):
        return self.email

    
from django.conf import settings


class ConnectionHistory(models.Model):
    ONLINE = 'online'
    OFFLINE = 'offline'
    STATUS = (
        (ONLINE, 'On-line'),
        (OFFLINE, 'Off-line'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    device_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS,default=ONLINE)
    first_login = models.DateTimeField(default=datetime.datetime.now)
    last_echo = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        unique_together = (("user", "device_id"),)