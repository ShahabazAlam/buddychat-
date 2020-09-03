import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.core import serializers
from django.forms import model_to_dict

from .serializers import FriendSerializer,birthdayNotificationSerializer
from notifications.models import CustomNotification,birthdayNotification
from channels.db import database_sync_to_async
from django.db.models import Q
from friends.models import Friend
from user_accounts.models import ConnectionHistory
from newsfeeds.models import Status
import datetime
User = get_user_model()


class Friends(AsyncJsonWebsocketConsumer):

    async def fetchOnlineFriends(self):
        content = await self.fetch_online_friends()
        await self.send_json(content)

    async def fetchFriendsBirthday(self):
        content = await self.fetch_friends_birthday()
        await self.send_json(content)

    async def fetchFriendsStatus(self):
        content = await self.fetch_friends_status()
        await self.send_json(content)

    async def fetchStatusTimeOut(self):
        content = await self.check_status_timeout()
        await self.send_json(content)





# connect method
    async def connect(self):
        user = self.scope['user']
        grp = 'friends{}'.format(user.id)
        await self.accept()
        await self.channel_layer.group_add(grp, self.channel_name)

    async def disconnect(self, close_code):
        user = self.scope['user']
        grp = 'friends{}'.format(user.id)
        await self.channel_layer.group_discard(grp, self.channel_name)

    async def notify(self, event):
        await self.send_json(event)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        data = json.loads(text_data)
        if data['command'] == 'fetch_online_friends':
            await self.fetchOnlineFriends()
        if data['command'] == 'fetch_friends_birthday':
            await self.fetchFriendsBirthday()
        if data['command'] == 'fetch_friends_status':
            await self.fetchFriendsStatus()
        if data['command'] == 'check_status_timeout':
            await self.fetchStatusTimeOut()

    @database_sync_to_async
    def fetch_online_friends(self):
        current_user = self.scope['user']
        user_friendship_id = Friend.objects.filter(status='friend',friend_id=current_user).values('user_id')
        friends_friendship_id = Friend.objects.filter(status='friend',user_id=current_user).values('friend_id')
        online_users = ConnectionHistory.objects.filter(status='online').values('user_id')
        friends_lists = User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id),id__in = online_users).values('id','first_name','last_name','profileImage','gender')
        serializer = FriendSerializer(friends_lists, many=True)
        content = {
            'command': 'online_friends_list',
            'online_friends': json.dumps(serializer.data)
        }
        return content


    @database_sync_to_async
    def fetch_friends_birthday(self):
        current_user = self.scope['user']
        notifications = birthdayNotification.objects.select_related('actor').filter(recipient=current_user, type="birthday", unread=True)
        serializer = birthdayNotificationSerializer(notifications, many=True)
        content = {
            'command': 'friend_birthday',
            'friend': json.dumps(serializer.data)
        }
        return content

    @database_sync_to_async
    def fetch_friends_status(self):
        current_user = self.scope['user']
        user_friendship_id = Friend.objects.filter(status='friend',friend_id=current_user).values('user_id')
        friends_friendship_id = Friend.objects.filter(status='friend',user_id=current_user).values('friend_id')
        friends_status = Status.objects.select_related('user').filter(Q(user_id__in=user_friendship_id)|Q(user_id__in=friends_friendship_id)|Q(user_id=current_user.id)).values('id',str('image'),'user__first_name','user__last_name',str('user__profileImage'),'user__gender','user__id')
        content = {
            'command': 'status_list',
            'status': json.dumps(list(friends_status))
        }
        return content


    @database_sync_to_async
    def check_status_timeout(self):
        all_status = Status.objects.all()
        for status in all_status:
        # If the expiration date is bigger than now delete it
            if status.expiration_date < datetime.datetime.now():
                id = status.id
                status.delete()
                content = {
                'command': 'status_time_out',
                'id': json.dumps(id)
                }
                return content