from django.db import models
from django.db import models
import datetime
from django.conf import settings

# Create your models here.
class MessageNotification(models.Model):
    type = models.CharField(default='message', max_length=30)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name='message_notifications',
        on_delete=models.CASCADE
    )
    unread = models.BooleanField(default=True, blank=False, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.now, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    ncounter = models.TextField(default=1) 



class CustomNotification(models.Model):
    type = models.CharField(default='friend_request', max_length=30)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    unread = models.BooleanField(default=True, blank=False, db_index=True)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        on_delete=models.CASCADE
    )

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    timestamp = models.DateTimeField(default = datetime.datetime.now, db_index=True)

    deleted = models.BooleanField(default=False, db_index=True)
    send = models.BooleanField(default=False, db_index=True)


class commentLikeNotifications(models.Model):
    type = models.CharField(default='post', max_length=30)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name='post_notifications',
        on_delete=models.CASCADE
    )
    postId = models.IntegerField()
    unread = models.BooleanField(default=True, blank=False, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.now, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True) 
    n_o_c = models.IntegerField()



class birthdayNotification(models.Model):
    type = models.CharField(default='birthdat_notifications', max_length=30)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        related_name='birthdat_notifications',
        on_delete=models.CASCADE
    )
    unread = models.BooleanField(default=True, blank=False, db_index=True)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        on_delete=models.CASCADE
    )

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    timestamp = models.DateTimeField(default=datetime.datetime.now, db_index=True)

    deleted = models.BooleanField(default=False, db_index=True)
    send = models.BooleanField(default=False, db_index=True)