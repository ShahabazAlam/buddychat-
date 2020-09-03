import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer,WebsocketConsumer
from django.contrib.auth import get_user_model
from django.core import serializers

from notifications.models import CustomNotification
from friends.serializers import NotificationSerializer
from communications.serializers import MessageNotificationSerializer
from channels.db import database_sync_to_async
from notifications.models import MessageNotification
from notifications.models import commentLikeNotifications
from newsfeeds.serializers import postNotificationSerializer
User = get_user_model()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    # friend request related notifications functions
    async def fetch_messages(self):
        content = await self.fetch_notifications()
        await self.send_json(content)
    
    async def fetch_read_messages(self):
        content = await self.fetch_read_notifications()
        await self.send_json(content)

    async def remove_all_unread_notifications(self):
        content = await self.remove_unread_notifications()
        await self.send_json(content)

    async def remove_all_read_notifications(self):
        content = await self.remove_read_notifications()
        await self.send_json(content)
    
    # messages related notifications functions
    async def fetch_messages_notifications(self):
        content = await self.fetch_msg_notifications()
        await self.send_json(content)

    # messages related notifications functions
    async def commentLikeNotifications(self):
        content = await self.comment_like_notifications()
        await self.send_json(content)

    async def readCommentLikeNotifications(self):
        content = await self.read_comment_like_notifications()
        await self.send_json(content)





#-------------------------------------------------------------------------------------------------
    # connect functions
    async def connect(self):
        user = self.scope['user']
        grp = 'all_notifications{}'.format(user.id)
        await self.accept()
        await self.channel_layer.group_add(grp, self.channel_name)


    # disconnect functions
    async def disconnect(self, close_code):
        user = self.scope['user']
        grp = 'all_notifications{}'.format(user.id)
        await self.channel_layer.group_discard(grp, self.channel_name)
        
    # notify functions
    async def notify(self, event):
        await self.send_json(event)


    # recieve functions
    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        data = json.loads(text_data)
        # friend requests related notifications command
        if data['command'] == 'fetch_friends_notifications':
            await self.fetch_messages()
        if data['command'] == 'fetch_read_friends_notifications':
            await self.fetch_read_messages()
        if data['command'] == 'remove_all_unread_notifications':
            await self.remove_all_unread_notifications()
        if data['command'] == 'remove_all_read_notifications':
            await self.remove_all_read_notifications()
        # message  notifications command
        if data['command'] == 'fetch_messages_notifications':
            await self.fetch_messages_notifications()

        # other  notifications command
        if data['command'] == 'fetch_comment_like_notifications':
            await self.commentLikeNotifications()

        if data['command'] == 'fetch_read_cl_notifications':
            await self.readCommentLikeNotifications()   



    
    # friend requests related queries functions
    @database_sync_to_async
    def fetch_notifications(self):
        user = self.scope['user']
        notifications = CustomNotification.objects.select_related('actor').filter(recipient_id=user.id, type="friend", unread=True)
        serializer = NotificationSerializer(notifications, many=True)
        content = {
            'command': 'notifications',
            'notifications': json.dumps(serializer.data)
        }
        return content

    @database_sync_to_async
    def fetch_read_notifications(self):
        user = self.scope['user']
        notifications = CustomNotification.objects.select_related('actor').filter(recipient_id=user.id, type="friend", unread=False)
        serializer = NotificationSerializer(notifications, many=True)
        content = {
            'command': 'read_notifications',
            'notifications': json.dumps(serializer.data)
        }
        return content

    @database_sync_to_async
    def remove_unread_notifications(self):
        user = self.scope['user']
        notifications = CustomNotification.objects.select_related('actor').filter(recipient_id=user.id, type="friend", unread=True).delete()
        if notifications:
            content = {
                'command': 'removed_unread_notifications',
            }
        return content
        

    @database_sync_to_async
    def remove_read_notifications(self):
        user = self.scope['user']
        notifications = CustomNotification.objects.select_related('actor').filter(recipient_id=user.id, type="friend", unread=False).delete()
        if notifications:
            content = {
                'command': 'removed_read_notifications',
            }
        return content

    # messages related queries functions
    @database_sync_to_async
    def fetch_msg_notifications(self):
        user = self.scope['user']
        notifications = MessageNotification.objects.select_related('actor').filter(recipient_id=user.id, type="message", unread=True)
        serializer = MessageNotificationSerializer(notifications, many=True)
        content = {
            'command': 'message_notifications',
            'message_notifications': json.dumps(serializer.data),
        }
        return content

    # messages related queries functions
    @database_sync_to_async
    def comment_like_notifications(self):
        user = self.scope['user']
        notifications = commentLikeNotifications.objects.select_related('actor').filter(recipient_id=user.id, unread=True)
        serializer = postNotificationSerializer(notifications, many=True)
        content = {
            'command': 'comment_like_notifications',
            'cl_notifications': json.dumps(serializer.data),
        }
        return content

    @database_sync_to_async
    def read_comment_like_notifications(self):
        user = self.scope['user']
        notifications = commentLikeNotifications.objects.select_related('actor').filter(recipient_id=user.id, unread=False)
        serializer = postNotificationSerializer(notifications, many=True)
        content = {
            'command': 'cl_readed_notifications',
            'notifications': json.dumps(serializer.data)
        }
        return content