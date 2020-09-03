from django.shortcuts import render
from user_accounts.models import User
from .models import Post,Like,Comment,Gallery,commentLike,Status
from notifications.models import commentLikeNotifications
from django.http import JsonResponse,HttpResponse
from django.views.generic import ListView,View,TemplateView,RedirectView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import update_session_auth_hash
from django.contrib import auth
from django.urls import reverse_lazy
import os
from friends.models import Friend
from user_accounts.models import User
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
from django.db.models import Q,F
from django.core import serializers
from .serializers import postNotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from newsfeeds.models import Status
# Start////////////
from django.forms import model_to_dict
from django.db.models import Model

class ExtendedEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            return model_to_dict(o)
        return super().default(o)



@login_required(login_url=reverse_lazy("user_accounts:login"))
@csrf_exempt
def savePost(request):
    if request.is_ajax():        
        if request.POST.get('body'):
            body = request.POST.get('body')
        else:
            body = None
        if request.POST.get('page'):
            page = request.POST.get('page')
        else:
            page = request.user.id
        if request.FILES.get('images[]') or body:
            if not os.path.exists('media/postThumbnail'):
                os.makedirs('media/postThumbnail')
            if not request.FILES.get('images[]'):
                status = request.POST.get('status')
                obj = Post.objects.create(body=body,status=status,user_id=request.user.id,page=page)
                data = {
                   'success':'success'
                }
            else:
                status = request.POST.get('status')
                myfile =request.FILES.get('images[]')               
                fs = FileSystemStorage("media/postThumbnail")
                filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
                fs.url(filename) 
                obj = Post.objects.create(body=body,thumbnail=filename,status=status,user_id=request.user.id,page=page)
                data = {
                    'success':'success'
                }
        if len(request.FILES.getlist('images[]')) > 1:
            if not os.path.exists('media/postGallery'):
                os.makedirs('media/postGallery')
            fs = FileSystemStorage("media/postGallery")
            for myfile in request.FILES.getlist('images[]'):              
                filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
                fs.url(filename)
                gallery = Gallery(post_id=obj.id, images=filename)
                gallery.save()
                data = {
                   'success':'success'
                }
        return HttpResponse(data)  
from django.forms.models import model_to_dict     
 
class fetchPosts(LoginRequiredMixin,View):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if request.GET.get('page_id'):
            page = request.GET.get('page_id') 
            qs = Post.objects.filter(Q(page = page)|Q(user_id=page)).values('id','page','body','thumbnail','status','comment_enabled','created_at','updated_at','user__first_name','user__last_name','user__profileImage','user__gender','user__id').order_by('-id')
            posts = json.dumps(list(qs),indent=2,cls=MyEncoder)
            return HttpResponse(posts)
        else:
            user_friendship_id = Friend.objects.filter(friend_id=self.request.user.id,status='friend').values('user_id')
            friends_friendship_id = Friend.objects.filter(user_id=self.request.user.id,status='friend').values('friend_id')
            friends_lists =User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id)).values('id')
            f_post = Post.objects.filter(Q(status='Every one')|Q(status='Friends'),user_id__in = friends_lists).values('id','page','body','thumbnail','status','comment_enabled','created_at','updated_at','user__first_name','user__last_name','user__profileImage','user__gender','user__id')
            my_post =Post.objects.filter(user_id=self.request.user.id).values('id','page','body','thumbnail','status','comment_enabled','created_at','updated_at','user__first_name','user__last_name','user__profileImage','user__gender','user__id')
            qs = my_post.union(f_post,all=True).order_by('-created_at')
            posts = json.dumps(list(qs),indent=2,cls=MyEncoder)
            return HttpResponse(posts)

class MyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d %I:%M:%S.%f")
        return super(MyEncoder, self).default(obj)
        
class addComment(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if request.is_ajax():  
            post_id = self.request.GET.get('id')
            noc = self.request.GET.get('noc')
            if post_id and noc :
                all_comments = Comment.objects.filter(post_id = post_id).values('id')
                if int(noc) == 1:
                    prev_noc = int(noc) - 1 
                    data = Comment.objects.filter(post_id = post_id).values('id','content','comment_image','updated_at','user__first_name','user__last_name','user__profileImage','user__id','user__gender','post__user_id').order_by('-created_at')[int(prev_noc):int(noc)]
                    comments = json.dumps({'comments':list(data),'NOC':len(all_comments)}, indent=2,cls=MyEncoder)
                    return HttpResponse(comments)
                else:
                    prev_noc = int(noc) - 5
                    data = Comment.objects.filter(post_id = post_id).values('id','content','comment_image','updated_at','user__first_name','user__last_name','user__profileImage','user__id','user__gender','post__user_id').order_by('-created_at')[int(prev_noc):int(noc)]
                    comments = json.dumps({'comments':list(data),'NOC':len(all_comments)}, indent=2,cls=MyEncoder)
                    return HttpResponse(comments)

    def post(self,request):
        if request.is_ajax():        
            if self.request.POST.get('content'):
                content = self.request.POST.get('content')
            else:
                content = None
                
            if self.request.FILES.get('comment_image') or content:
                post_id = self.request.POST.get('id')
                if not os.path.exists('media/postMedia'):
                    os.makedirs('media/postMedia')
                if not request.FILES.get('comment_image'):
                    Comment.objects.create(content=content,post_id=post_id,user_id=request.user.id)
                    data = {
                    'success':'success'
                    }
                else:
                    myfile = self.request.FILES.get('comment_image')               
                    fs = FileSystemStorage("media/postMedia")
                    filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
                    fs.url(filename) 
                    obj = Comment.objects.create(content=content,comment_image=filename,post_id=post_id,user_id=request.user.id)
                    data = {
                        'success':'success'
                    }


                if data:
                    # comment notification 
                    posted_user = Post.objects.get(id=post_id)
                    users = Comment.objects.filter(post_id = post_id).values('user').distinct().exclude(user_id=posted_user.user_id)

                    recipients = [] 

                    # add all users who commented the same object to recipients 
                    for u in users: 
                        if u not in recipients and u['user'] != request.user.id: 
                            recipients.append(u['user']) 
                        elif posted_user.user_id != request.user.id:
                            recipients.append(posted_user.user_id)
                            
                    for user in recipients:
                        channel_layer = get_channel_layer()
                        channel = "all_notifications{}".format(user)
                        if user == posted_user.user_id:
                            verb = 'commented on your post'
                        else:
                            verb = 'commented on his post'

                        if not commentLikeNotifications.objects.filter(type="comment" ,postId=post_id , recipient_id = user, actor=request.user).exists():
                            notification = commentLikeNotifications.objects.create(type="comment",postId=post_id , recipient_id = user, actor=request.user, verb=verb,n_o_c=1)
                            if notification:
                                async_to_sync(channel_layer.group_send)(
                                    channel, {
                                        "type": "notify",  # method name
                                        "command": "new_cl_notification",
                                        "cl_notifications": json.dumps(postNotificationSerializer(notification).data)
                                    }
                                )
                        else:
                            d = commentLikeNotifications.objects.filter(type="comment", postId=post_id , recipient_id = user, actor=request.user).update(n_o_c=F('n_o_c')+1,timestamp=datetime.datetime.now())
                            if d:    
                                notification = commentLikeNotifications.objects.get(type="comment", postId=post_id , recipient_id = user, actor=request.user)
                                async_to_sync(channel_layer.group_send)(
                                channel, {
                                    "type": "notify",  # method name
                                    "command": "new_existing_comment_notification",
                                    'id':json.dumps(notification.id),
                                    'timestamp':json.dumps(notification.timestamp, indent=2, cls=MyEncoder),
                                    }
                                )
                # end comments notifications
                return HttpResponse(data)


class fetchGalleryImages(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            id = request.GET.get('id')
            data = Gallery.objects.filter(post_id=id).values('images').order_by('-id')
            gallery = json.dumps(list(data),indent=2)
            return HttpResponse(gallery)

class likePost(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            post_id = request.GET.get('id')
            totalLikes = Like.objects.filter(post_id=post_id).values('user_id','user__first_name','user__last_name','user__profileImage','user__gender')
            return HttpResponse(json.dumps(list(totalLikes),indent=2))

    def post(self,request):
        if self.request.is_ajax():
            post_id = request.POST.get('id')
            posted_user = Post.objects.get(id=post_id)
            if not Like.objects.filter(post_id = post_id, user_id = request.user.id).exists():
                like  = Like.objects.create(post_id = post_id, user_id = request.user.id)
                like.save()
                if posted_user.user != request.user:
                    notification = commentLikeNotifications.objects.create(type="like",postId=post_id, recipient=posted_user.user, actor=request.user, verb="liked your post",n_o_c=1)
                    if notification:    
                        channel_layer = get_channel_layer()
                        channel = "all_notifications{}".format(posted_user.user_id)
                        async_to_sync(channel_layer.group_send)(
                            channel, {
                                "type": "notify",  # method name
                                "command": "new_cl_notification",
                                "cl_notifications": json.dumps(postNotificationSerializer(notification).data)
                            }
                        )
                data = {
                    'success':'success'
                }
            else:
                like = Like.objects.get(post_id = post_id, user_id = request.user.id)
                like.delete()
                data = commentLikeNotifications.objects.get(type="like",postId=post_id, recipient=posted_user.user, actor=request.user)
                d = commentLikeNotifications.objects.filter(type="like",postId=post_id, recipient=posted_user.user, actor=request.user).delete()
                if d:
                    channel_layer = get_channel_layer()
                    channel = "all_notifications{}".format(posted_user.user_id)
                    async_to_sync(channel_layer.group_send)(
                        channel, {
                            "type": "notify",  # method name
                            "command": "disliked_post_notification",
                            'id':json.dumps(data.id)
                        }
                    )
                data={
                    'success':'success'
                }
            return HttpResponse(data)

class nocLikeComment(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            post_id = request.GET.get('id')
            totalLikes = Like.objects.filter(post_id=post_id).values('id')
            all_comments = Comment.objects.filter(post_id = post_id).values('id')
            data = json.dumps({'NOL':len(totalLikes),'NOC':len(all_comments)}, indent=2,cls=MyEncoder)
            return HttpResponse(list(data))


class checkLike(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            post_id = request.GET.get('id')
            if not Like.objects.filter(post_id=post_id).exists():
                data = {
                    'no'
                }
            else:
                data = {
                    'yes'
                }
            return HttpResponse(data)


class disableComment(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            post_id = request.GET.get('id')
            post = Post.objects.get(id=post_id)
            if post.comment_enabled == 'enabled':
                post.comment_enabled = 'disabled'
                post.save()
                data = {
                    'success'
                }
            elif post.comment_enabled == 'disabled':
                post.comment_enabled = 'enabled'
                post.save()
                data = {
                    'success'
                }
            return HttpResponse(data)

class checkEnableDisableComment(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            post_id = request.GET.get('id')
            post = Post.objects.get(id=post_id)
            if post.comment_enabled == 'enabled':
                data = {
                    'enabled'
                }
            elif post.comment_enabled == 'disabled':
                data = {
                    'disabled'
                }
            return HttpResponse(data)

class deletePost(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            post_id = request.GET.get('id')
            if Post.objects.filter(id=post_id).exists():
                post = Post.objects.get(id=post_id)
                post.delete()
                data = {
                    'success'
                }
            return HttpResponse(data)


class updatePost(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            post_id = request.GET.get('id')
            updated_text = request.GET.get('updated_text')
            if Post.objects.filter(id=post_id).exists():
                post = Post.objects.get(id=post_id)
                post.body = updated_text
                post.save()
                data = {
                    'success'
                }
            return HttpResponse(data)


class deleteComment(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            comment_id = self.request.GET.get('id')
            if Comment.objects.filter(id=comment_id).exists():
                comment = Comment.objects.get(id=comment_id)
                comment.delete()
                data = {
                    'success'
                }
            return HttpResponse(data)

class updateComment(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            comment_id = request.GET.get('id')
            updated_text = request.GET.get('updated_text')
            if Comment.objects.filter(id=comment_id).exists():
                comment = Comment.objects.get(id=comment_id)
                comment.content = updated_text
                comment.save()
                data = {
                    'success'
                }
            return HttpResponse(data)

class likeComment(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def post(self,request):
        if self.request.is_ajax():
            c_id = request.POST.get('id')
            if not commentLike.objects.filter(comment_id = c_id, user_id = request.user.id).exists():
                like  = commentLike.objects.create(comment_id = c_id, user_id = request.user.id)
                like.save()
                data = {
                    'success':'success'
                }
            else:
                like  = commentLike.objects.filter(comment_id = c_id, user_id = request.user.id)
                like.delete()
                data={
                    'success':'success'
                }
            return HttpResponse(data)


class checkCommentLike(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request):
        if self.request.is_ajax():
            c_id = request.GET.get('id')
            if not commentLike.objects.filter(comment_id=c_id).exists():
                data = {
                    'no'
                }
            else:
                data = {
                    'yes'
                }
            return HttpResponse(data)

@login_required(login_url=reverse_lazy("user_accounts:login"))
def getName(request):
    page_id = request.GET.get('page_id')
    user = User.objects.get(id = page_id)
    return JsonResponse({
        'f_name':user.first_name,
        'l_name':user.last_name
    })

@login_required(login_url=reverse_lazy("user_accounts:login"))
@csrf_exempt
def saveStatus(request):
    if request.is_ajax():
        if not os.path.exists('media/statusMedia'):
            os.makedirs('media/statusMedia')
        myfile = request.FILES.get('status_img')               
        fs = FileSystemStorage("media/statusMedia")
        filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
        fs.url(filename) 
        obj = Status.objects.create(user=request.user,image=filename,expiration_date=timezone.now() + datetime.timedelta(days=1))
        if obj:
            data = {
                'id':obj.id,
                'image':str(obj.image),
                'user__first_name':obj.user.first_name,
                'user__last_name':obj.user.last_name,
                'user__profileImage':str(obj.user.profileImage),
                'user__gender':obj.user.gender,
                'user__id':obj.user.id
            }
            channel_layer = get_channel_layer()
            current_user = request.user.id
            user_friendship_id = Friend.objects.filter(status='friend',friend_id=current_user).values('user_id')
            friends_friendship_id = Friend.objects.filter(status='friend',user_id=current_user).values('friend_id')
            friends_lists = User.objects.filter(Q(id__in=user_friendship_id)|Q(id__in=friends_friendship_id)|Q(id=current_user)).values('id')
            for friend in friends_lists:
                channel = "friends{}".format(friend['id'])
                async_to_sync(channel_layer.group_send)(
                    channel, {
                        "type": "notify",  # method name
                        "command": "new_status_created",
                        'data':json.dumps(data,cls=ExtendedEncoder)
                    }
                )
            return HttpResponse({'success':'success'})

@login_required(login_url=reverse_lazy("user_accounts:login"))
def deleteStatus(request):
    s_id = request.GET.get('s_id')
    status = Status.objects.filter(id = s_id).delete()
    return JsonResponse({'success':'success'})

@login_required(login_url=reverse_lazy("user_accounts:login"))
def searchData(request):
    input = request.GET.get('input')
    if input:
        user = User.objects.filter(Q(first_name__icontains=input)|Q(last_name__icontains=input)).exclude(id=request.user.id).values('id','first_name','last_name',str('profileImage'),'gender')
    else:
        user = ''
    return HttpResponse(json.dumps(list(user)))