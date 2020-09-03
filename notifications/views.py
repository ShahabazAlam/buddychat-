from django.http import JsonResponse
from django.shortcuts import render
from newsfeeds.models import Post,Comment,Like
from notifications.models import CustomNotification,commentLikeNotifications,birthdayNotification
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

class MyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d %I:%M:%S.%f")
        return super(MyEncoder, self).default(obj)


@login_required(login_url=reverse_lazy("user_accounts:login"))
def mark_all_notifications_as_read(request):
    CustomNotification.objects.filter(recipient=request.user, type="comment").update(unread=False)
    return JsonResponse({
        'status': True,
        'message': "Marked all notifications as read"
    })

    

@login_required(login_url=reverse_lazy("user_accounts:login"))
def mark_notification_as_read(request):
    id = request.GET.get('id')
    CustomNotification.objects.filter(id=id).update(unread=False)
    return JsonResponse({
        'message': "success"
    })



@login_required(login_url=reverse_lazy("user_accounts:login"))
def readOneComment(request,post_id,cl_id):
    commentLikeNotifications.objects.filter(id=cl_id).delete()
    return render(request,'commentNotifications/readcomment.html',{'post_id':post_id})

# read one comment notification actions
@login_required(login_url=reverse_lazy("user_accounts:login"))
def readComment(request):
    post_id = request.GET.get('post_id')
    if request.is_ajax():
        post = Post.objects.get(id=post_id)
        data = {
            'id':post.id,
            'body':post.body,
            'thumbnail':str(post.thumbnail),
            'status':post.status,
            'comment_enabled':post.comment_enabled,
            'updated_at':post.updated_at,
            'first_name':post.user.first_name,
            'last_name':post.user.last_name,
            'd_p':str(post.user.profileImage),
            'gender':post.user.gender,
            'user_id':post.user.id

        }
    return JsonResponse(data)

# read one comment notification actions
@login_required(login_url=reverse_lazy("user_accounts:login"))
def readBirthdayNotification(request):
    b_id = request.GET.get('b_id')
    if request.is_ajax():
        delete = birthdayNotification.objects.filter(id=b_id).update(unread=False)
        if delete:
            return JsonResponse({'success':'success'})