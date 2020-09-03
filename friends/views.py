from django.shortcuts import render
import json
from user_accounts.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse,HttpResponse
from django.views.generic import ListView,View,TemplateView
from friends.serializers import NotificationSerializer,UserSerializer
from friends.models import Friend,Block
from notifications.models import CustomNotification
import datetime
from django.db.models import Q
from Profile.models import user_Detail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy 
from django.contrib.auth.mixins import LoginRequiredMixin

enco = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
    )

class FindFriendsListView(LoginRequiredMixin,TemplateView):
    login_url = '/user_accounts/login/'
    template_name = "friends/find-friends.html"
        
class SuggestFriends(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            user_friendship_id = Friend.objects.filter(status='friend',friend_id=self.request.user.id).values('user_id')
            friends_friendship_id = Friend.objects.filter(status='friend',user_id=self.request.user.id).values('friend_id')
            user_block_id = Block.objects.filter(friend_id=self.request.user.id).values('user_id')
            friend_block_id = Block.objects.filter(user_id=self.request.user.id).values('friend_id')
            get_request = list(Friend.objects.filter(Q(user=self.request.user.id) & Q(status='requested')).values_list('friend_id', flat=True))
            sent_request = list(Friend.objects.filter(Q(friend_id=self.request.user.id) & Q(status='requested')).values_list('user_id', flat=True))
            users_list = User.objects.exclude(id__in=user_block_id).exclude(id__in=friend_block_id).exclude(id__in=friends_friendship_id).exclude(id__in=user_friendship_id).exclude(id__in=get_request).exclude(id__in=sent_request).exclude(id=self.request.user.id).values().order_by('-date_joined')
            data = json.dumps(list(users_list), indent=2,default=enco)
            return HttpResponse(data)

# send request method      
@login_required(login_url=reverse_lazy("user_accounts:login"))
def send_request(request, id=None):
    if request.is_ajax():
        if id is not None:
            friend_user = User.objects.get(id=id)
            Friend.objects.create(user=request.user, friend=friend_user)
            notification = CustomNotification.objects.create(type="friend", recipient=friend_user, actor=request.user, verb="sent you friend request")
            channel_layer = get_channel_layer()
            channel = "all_notifications{}".format(friend_user.id)
            async_to_sync(channel_layer.group_send)(
                channel, {
                    "type": "notify",  # method name
                    "command": "new_friend_request_notification",
                    "notification": json.dumps(NotificationSerializer(notification).data)
                }
            )
            data = {
                'success': "success"
            }
            return HttpResponse(data)

# accept friend request method
@login_required(login_url=reverse_lazy("user_accounts:login"))
def accept_request(request, id=None):
    if id is not None:
        if request.is_ajax():
            friend_user = User.objects.get(id=id)
            current_user = request.user
            f = Friend.objects.filter(user=friend_user, friend=current_user, status='requested')[0]
            f.status = "friend"
            f.save()
            CustomNotification.objects.filter(recipient=current_user, actor=friend_user, type='friend').update(unread=False)
            notification = CustomNotification.objects.create(type="friend", recipient=friend_user, actor=request.user, verb="accepted your friend request")
            channel_layer = get_channel_layer()
            channel = "all_notifications{}".format(friend_user.id)
            async_to_sync(channel_layer.group_send)(
                channel, {
                    "type": "notify",  # method name
                    "command": "new_accept_request_notification",
                    "notification": json.dumps(NotificationSerializer(notification).data)
                }
            )
            data = {
                'success': "success",
            }
            return HttpResponse(data)


# cancle friend request method
@login_required(login_url=reverse_lazy("user_accounts:login"))
def Cancel_Request(request, id=None):
    if id is not None:
        if request.is_ajax():
            friend_user = User.objects.get(id=id)
            current_user = request.user
            f = Friend.objects.filter(Q(user=friend_user, friend=current_user)|Q(friend=friend_user, user=current_user), status='requested')
            f.delete()
            CustomNotification.objects.filter(recipient=current_user, actor=friend_user, type='friend').update(unread=False)
            data = {
                'success': "success",
            }
            return HttpResponse(data)

    

class RequestList(LoginRequiredMixin,View):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            current_user = self.request.user.id
            requests = Friend.objects.filter(status='requested',friend_id=current_user).values('user_id')
            requests_lists =User.objects.filter(id__in=requests).values()
            enco = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime.datetime)
            or isinstance(obj, datetime.date)
            else None
            )
            requested_friends_data = json.dumps(list(requests_lists), indent=2,default=enco)
            return HttpResponse(requested_friends_data)



class yourFriends(LoginRequiredMixin,View):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            current_user = self.request.user.id
            user_friendship_id = Friend.objects.filter(status='friend',friend_id=current_user).values('user_id')
            friends_friendship_id = Friend.objects.filter(status='friend',user_id=current_user).values('friend_id')
            friends_lists =User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id)).values('id','profileImage','gender','first_name','last_name')
            enco = lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime.datetime)
            or isinstance(obj, datetime.date)
            else None
            )
            friends_data = json.dumps(list(friends_lists), indent=2,default=enco)
            return HttpResponse(friends_data)

#unfriend user method
@login_required(login_url=reverse_lazy("user_accounts:login"))
def Unfriend(request, id=None):
    if id is not None:
        if request.is_ajax():
            friend_user = User.objects.get(id=id)
            current_user = request.user
            if not Friend.objects.filter(friend=friend_user, user=current_user, status='friend').exists():
                f = Friend.objects.filter(user=friend_user, friend=current_user, status='friend')
                f.delete()
            else:
                f = Friend.objects.filter(friend=friend_user, user=current_user, status='friend')
                f.delete()
            data = {
               'success': "success",
            }
            return HttpResponse(data)

#block user method
@login_required(login_url=reverse_lazy("user_accounts:login"))
def BlockUser(request, id=None):
    if id is not None:
        if request.is_ajax():
            friend_user = User.objects.get(id=id)
            friend1 = Friend.objects.filter(
                Q(user_id=request.user.id),Q(friend_id=friend_user.id))
            if friend1:
                friend1.delete()
                block = Block.objects.create(user_id=request.user.id, friend_id=friend_user.idr)
            else:
                friend2 = Friend.objects.filter(
                Q(user_id=friend_user.id),Q(friend_id=request.user.id))
                friend2.delete()
                block = Block.objects.create(user_id=friend_user.id,friend_id = request.user.id)
            data = {
                'success': "success",
            }
            return HttpResponse(data)

# fetch friend list method
@login_required(login_url=reverse_lazy("user_accounts:login"))
@csrf_exempt
def getFriendFriendList(request,id):
    if request.is_ajax():
        current_user = id
        user_friendship_id = Friend.objects.filter(status='friend',friend_id=current_user).values('user_id')
        friends_friendship_id = Friend.objects.filter(status='friend',user_id=current_user).values('friend_id')
        friends_lists =User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id)).values('id')
        friends = User.objects.filter(id__in = friends_lists).values('first_name','last_name','coverImage','profileImage','gender','id').order_by('-id')[:10]

        friends_data = json.dumps(list(friends), indent=2,default=enco)
        return HttpResponse(friends_data)


#load all friends method
@login_required(login_url=reverse_lazy("user_accounts:login"))
def loadAllFriend(request,id):
    current_user = request.user
    friend_id = User.objects.get(id=id)

    user_block_id = Block.objects.filter(friend_id=request.user.id).values('user_id')
    friend_block_id = Block.objects.filter(user_id=request.user.id).values('friend_id')
    
    user_friendship_id = Friend.objects.filter(friend_id=friend_id.id).values('user_id')
    friends_friendship_id = Friend.objects.filter(user_id=friend_id.id).values('friend_id')
    friends_lists =User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id)).values('id')
    friend_friends = User.objects.filter(id__in = friends_lists).exclude(id__in=user_block_id).exclude(id__in=friend_block_id).values('id','first_name','last_name','coverImage','profileImage','id','gender').order_by('-id')
    return render(request,'friends/all-friend.html',{'friends_data':friend_friends})


#load block users method
@login_required(login_url=reverse_lazy("user_accounts:login"))
def loadBlockedUsers(request):
    if request.is_ajax():
        current_user = request.user.id
        user_blocked_id = Block.objects.filter(friend_id=current_user).values('user_id')
        friends_blocked_id = Block.objects.filter(user_id=current_user).values('friend_id')
        blocked_lists =User.objects.filter(Q(id__in=user_blocked_id)|Q(id__in=friends_blocked_id)).values('id')
        blocked = User.objects.filter(id__in = blocked_lists).values('first_name','last_name','coverImage','profileImage','gender','id').order_by('-id')[:10]

        blocked_data = json.dumps(list(blocked), indent=2,default=enco)
        return HttpResponse(blocked_data)


# unblock user method
@login_required(login_url=reverse_lazy("user_accounts:login"))
def unblockUsers(request,id):
    if request.is_ajax():
            friend_user = User.objects.get(id=id)
            current_user = request.user.id
            if not Block.objects.filter(friend_id=friend_user.id, user_id=current_user,status='block').exists():
                f = Block.objects.filter(user_id=friend_user.id, friend_id=current_user, status='block')
                f.delete()
            else:
                f = Block.objects.filter(friend_id=friend_user, user_id=current_user, status='block')
                f.delete()
            data = {
                'success': "success",
            }
            return HttpResponse(data)

