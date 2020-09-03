import json

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.core import serializers
from django.forms import model_to_dict
from .models import ConnectionHistory
from django.db.models import F,Q
import datetime
from friends.models import Friend
User = get_user_model()
from friends.serializers import FriendSerializer
from asgiref.sync import async_to_sync,sync_to_async
from channels.layers import get_channel_layer
from Profile.models import user_Detail
from notifications.models import birthdayNotification


class OnlineCheckConsumer(WebsocketConsumer):
    def connect(self):
        current_user = self.scope['user']
        #user online concept
        user_friendship_id = Friend.objects.filter(status='friend',friend_id=current_user).values('user_id')
        friends_friendship_id = Friend.objects.filter(status='friend',user_id=current_user).values('friend_id')
        friends_lists = User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id)).values('id')
        for friend in friends_lists:
            channel_layer = get_channel_layer()
            channel = "friends{}".format(friend['id'])
            async_to_sync(channel_layer.group_send)(
                channel, {
                    "type": "notify",  # method name
                    "command": "friend_login",
                    'user':json.dumps({'id':current_user.id,'first_name':current_user.first_name,'last_name':current_user.last_name,'profileImage':str(current_user.profileImage),'gender':current_user.gender})
                }
            )
        #user birthday concept
        if user_Detail.objects.filter(user_id = current_user.id).exists():
            year_month = datetime.datetime.now()
            only_year_month = year_month.strftime("%m-%d")
            dob_qry = user_Detail.objects.get(user_id = current_user.id)
            user_dob = dob_qry.dob
            dob = user_dob.strftime("%m-%d")
            if(dob == only_year_month):
                for friend in friends_lists:
                    if not  birthdayNotification.objects.filter(recipient_id=friend['id'], actor_id=current_user.id,).exists():
                        birthdayNotification.objects.create(type="birthday", recipient_id=friend['id'], actor_id=current_user.id, verb="have birthday today")

        self.accept()
    
    def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        deviceInfo =  data['deviceInfo']
        self.update_user_status(user, 'online', deviceInfo)

    def disconnect(self, close_code):
        current_user = self.scope['user']
        user_friendship_id = Friend.objects.filter(status='friend',friend_id=current_user).values('user_id')
        friends_friendship_id = Friend.objects.filter(status='friend',user_id=current_user).values('friend_id')
        friends_lists = User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id)).values('id')
        for friend in friends_lists:
            channel_layer = get_channel_layer()
            channel = "friends{}".format(friend['id'])
            async_to_sync(channel_layer.group_send)(
                channel, {
                    "type": "notify",  # method name
                    "command": "friend_logout",
                    'id':json.dumps(current_user.id)
                }
            )
        data = ConnectionHistory.objects.get(user=current_user)
        deviceInfo = data.device_id
        self.update_user_status(current_user, 'offline',deviceInfo)

#send message to the frontend
    def notify(self, event):
        self.send(text_data=json.dumps(event["text"]))

    def update_user_status(self, user, status,device_id):
        if not ConnectionHistory.objects.filter(user=user):
            return ConnectionHistory.objects.create(user=user, device_id=device_id , status=status,last_echo=datetime.datetime.now())
        else:
            data = ConnectionHistory.objects.get(user=user)
            data.status = status
            data.last_echo = datetime.datetime.now()
            data.save()
            return data
    def update_user_incr(self, user):
        ConnectionHistory.objects.filter(pk=user.pk).update(online=F('online') + 1)

    def update_user_decr(self, user):
        ConnectionHistory.objects.filter(pk=user.pk).update(online=F('online') - 1)



