from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer, AsyncJsonWebsocketConsumer
import json
from django.db.models import Q,F
from .models import Message, Room
from user_accounts.models import ConnectionHistory
from communications.serializers import MessageNotificationSerializer
from notifications.models import MessageNotification
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
import datetime
User = get_user_model()


class MyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d %I:%M:%S.%f")
        return super(MyEncoder, self).default(obj)

class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room = None

    def fetch_messages(self, data):
        author = User.objects.get(id=data['author'])
        friend = User.objects.get(id=data['friend'])
        messages = Message.objects.filter(Q(author=author, friend=friend) | Q(author=friend, friend=author)).exclude(delete_user=author.id).order_by(
            'timestamp')[:20]
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        author = data['from']
        friend = data['friend']
        author_user = User.objects.get(id=author)
        friend_user = User.objects.get(id=friend)
        check_conn = Room.objects.get(Q(author=author_user, friend=friend_user) | Q(author=friend_user, friend=author_user))
        check_online = ConnectionHistory.objects.get(user_id=friend)
        if (check_conn.author_status == 'connected' and check_conn.friend_status == 'connected'):
            read_status = 'seen'
        elif ((check_conn.author_status == 'connected' or check_conn.friend_status == 'connected') and check_online.status == 'online'):
            read_status = 'delivered'
        elif ((check_conn.author_status == 'connected' or check_conn.friend_status == 'connected') and check_online.status == 'offline'):
            read_status = 'pending'

        if ((check_conn.author_status != 'connected' or check_conn.friend_status != 'connected') and (check_online.status == 'online' or check_online.status == 'offline')):
            channel_layer = get_channel_layer()
            channel = "all_notifications{}".format(friend_user.id)
            if not MessageNotification.objects.filter(type="message", recipient=friend_user, actor=author_user).exists():
                notification = MessageNotification.objects.create(type="message", recipient=friend_user, actor=author_user, verb="send you a new message!",ncounter=1)
                async_to_sync(channel_layer.group_send)(
                channel, {
                    "type": "notify",  # method name
                    "command": "new_message_notification",
                    "message_notification": json.dumps(MessageNotificationSerializer(notification).data)
                }
            )
            else:
                MessageNotification.objects.filter(type="message", recipient=friend_user, actor=author_user).update(ncounter=F('ncounter')+1,timestamp=datetime.datetime.now())
                notification = MessageNotification.objects.get(recipient=friend_user, actor=author_user)
                async_to_sync(channel_layer.group_send)(
                channel, {
                    "type": "notify",  # method name
                    "command": "new_existing_message_notification",
                    'id':json.dumps(notification.id),
                    'timestamp':json.dumps(notification.timestamp,cls=MyEncoder),
                }
            )
        message = Message.objects.create(
            author=author_user,
            friend=friend_user,
            room=self.room,
            message=data['message'],
            read_status = read_status)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def typing_start(self, data):
        author = data['from']
        author_user = User.objects.get(id=author)
        content = {
            'command': 'typing_start',
            'id': author,
            'd_p':author_user.profileImage,
            'gender':author_user.gender,
            'message': author_user.first_name +" "+ author_user.last_name
        }

        return self.send_chat_message(content)

    def typing_stop(self, data):
        content = {
            'command': 'typing_stop',
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    @staticmethod
    def message_to_json(message):
        return {
            'author': message.author.id,
            'friend': message.friend.id,
            'content': message.message,
            'm_id' : message.id,
            'read_status':message.read_status,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
        'typing_start': typing_start,
        'typing_stop': typing_stop,
    }

    def connect(self):
        self.user = self.scope['user']
        self.friendid = self.scope['url_route']['kwargs']['friendId']
        author_user = User.objects.get(id=self.user.id)
        friend_user = User.objects.get(id=self.friendid)

        if Room.objects.filter(
                Q(author=author_user, friend=friend_user) | Q(author=friend_user, friend=author_user)).exists():
            self.room = Room.objects.filter(
                Q(author=author_user, friend=friend_user) | Q(author=friend_user, friend=author_user))[0]
        else:
            self.room = Room.objects.create(author=author_user, friend=friend_user)
        self.room_group_name = 'chat_%s' % str(self.room.id)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        if Room.objects.filter(Q(author=author_user,friend_id=friend_user)).exists():
            Room.objects.filter(Q(author=author_user,friend_id=friend_user)).update(author_status='connected')
        else:
            Room.objects.filter(Q(author=friend_user,friend_id=author_user)).update(friend_status='connected')
        
        Message.objects.filter(Q(author=author_user, friend=friend_user) | Q(author=friend_user, friend=author_user)).update(read_status='seen')
        
        self.accept()

    def disconnect(self, close_code):
        self.user = self.scope['user']
        self.friendid = self.scope['url_route']['kwargs']['friendId']
        if Room.objects.filter(Q(author_id=self.user.id,friend_id=self.friendid)).exists():
            Room.objects.filter(Q(author_id=self.user.id,friend_id=self.friendid)).update(author_status='disconnected')
        else:
            Room.objects.filter(Q(author=self.friendid,friend_id=self.user.id)).update(friend_status='disconnected')
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
