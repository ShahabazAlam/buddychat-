import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from user_accounts.models import User
from friends.models import Friend
from communications.models import Room,Message
from notifications.models import MessageNotification
from django.db.models import Q
from django.http import JsonResponse,HttpResponse
from user_accounts.models import ConnectionHistory
import datetime
from datetime import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q


enco = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
    )
    
class MyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super(MyEncoder, self).default(obj)


@login_required(login_url=reverse_lazy("user_accounts:login"))
def all_messages(request):
    return render(request, "communications/friend-messages.html")



# Conversation with one friend
@login_required(login_url=reverse_lazy("user_accounts:login"))
def one_to_one_chat(request,id):
    f_data = User.objects.get(id=id)
    data = {
        'f_id': id,
        'u_id': request.user.id,
        'f_dp' :  f_data.profileImage,
        'f_gender' :  f_data.gender,
        'u_gender' : request.user.gender,
        'u_dp' : request.user.profileImage,
        'f_first_name' : f_data.first_name,
        'f_last_name' : f_data.last_name,
    }
    return render(request, "communications/friend-messages.html", {'data':data})


# get list of messages actions
@login_required(login_url=reverse_lazy("user_accounts:login"))
def friendList(request,id):
    friend_one = Room.objects.filter(author_id = request.user.id).values('friend_id')
    friend_two = Room.objects.filter(friend_id = request.user.id).values('author_id')
    friends = User.objects.filter(Q(id__in = friend_one) | Q(id__in = friend_two) ).values('id','first_name','last_name','profileImage','gender')
    data = json.dumps(list(friends), indent=2,default=enco)
    return JsonResponse(data,safe=False)


#check online actions
@login_required(login_url=reverse_lazy("user_accounts:login"))
def checkOnline(request):
    id = request.GET.get('id')
    check = ConnectionHistory.objects.get(user=id)
    date_time = (check.last_echo).strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {
        'status':check.status,
        'last_echo': date_time,
    }
    return JsonResponse(data)



# remove one message actions
@login_required(login_url=reverse_lazy("user_accounts:login"))
def deleteMessage(request):
    id = request.GET.get('id')
    check = Message.objects.filter(id=id).update(delete_user = request.user.id)
    if check:
        data ={
            'message':'success'
        }
    else:
        data ={
            'message':'failed'
        }
    return JsonResponse(data)




# message notifications actions
@login_required(login_url=reverse_lazy("user_accounts:login"))
def readMsgNotifications(request):
    id = request.GET.get('m_id')
    check = MessageNotification.objects.filter(id=id).delete()
    data ={
        'message':'success'
    }
    return JsonResponse(data)

# remove all notifications actions
@login_required(login_url=reverse_lazy("user_accounts:login"))
def removeAllNotifications(request):
    id = request.user
    check = MessageNotification.objects.filter(recipient=id).delete()
    data ={
        'message':'success'
    }
    return JsonResponse(data)

@login_required(login_url=reverse_lazy("user_accounts:login"))
def lastMessage(request):
    u_id = request.user
    f_id = request.GET.get('id')
    msg = Message.objects.filter(Q(author_id=u_id,friend_id=f_id)|Q(author_id=f_id,friend_id=u_id)).last()
    if msg:
        message = msg.message
    else:
        message = None
    return HttpResponse(message)

@login_required(login_url=reverse_lazy("user_accounts:login"))
def delectConversation(request):
    u_id = request.user
    f_id = request.GET.get('f_id')
    con = Message.objects.filter(Q(author_id=u_id,friend_id=f_id)|Q(author_id=f_id,friend_id=u_id)).delete()
    room = Room.objects.filter(Q(author_id=u_id,friend_id=f_id)|Q(author_id=f_id,friend_id=u_id)).delete()
    if room and con:
        return HttpResponse('success')