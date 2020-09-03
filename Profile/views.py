from django.shortcuts import render
from user_accounts.models import User
from .models import profile_Pic,cover_Pic,user_Detail
from newsfeeds.models import Gallery,Post
from django.http import JsonResponse,HttpResponse
from django.views.generic import ListView,View,TemplateView,RedirectView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import update_session_auth_hash
from django.contrib import auth
from django.urls import reverse_lazy
import os
import datetime
from django.db.models import Q
from newsfeeds.models import Post
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
from django.urls import resolve
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from friends.models import Friend

# Create your views here.

class MyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super(MyEncoder, self).default(obj)
        

class user_Timeline(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request,id):
        if user_Detail.objects.filter(user_id=id).exists():
            users = user_Detail.objects.get(user_id=id)
        else:
            users = ''
        user_data = User.objects.get(id=id)
        ImagesVideos = Post.objects.filter(user_id= id).values('thumbnail')[:6]
        ProfilePics = profile_Pic.objects.filter(user_id= id).values('profileImage')[:6]
        CoverPics = cover_Pic.objects.filter(user_id= id).values('coverImage')[:6]
        return render(request,'Profile/user_timeline.html',{'imagevideos':ImagesVideos,'coverPics':CoverPics,'profilePics':ProfilePics,'users':users,'user_data':user_data})

@login_required(login_url=reverse_lazy("user_accounts:login"))
@csrf_exempt
def profile_Pic_Save(request):
    if not os.path.exists('media/profileImages'):
        os.makedirs('media/profileImages')
    if request.is_ajax() and request.FILES['profileImage']:
        myfile = request.FILES['profileImage']
        fs = FileSystemStorage("media/profileImages")
        filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
        fs.url(filename)  # gets the url
        profile_Pic.objects.create(profileImage=filename, user_id=request.user.id)
        User.objects.filter(id=request.user.id).update(profileImage=filename)            
        return HttpResponse(filename)


@login_required(login_url=reverse_lazy("user_accounts:login"))
@csrf_exempt
def cover_Pic_Save(request):
    if not os.path.exists('media/coverImages'):
        os.makedirs('media/coverImages')
    if request.is_ajax() and request.FILES['coverImage']:
        myfile = request.FILES['coverImage']
        fs = FileSystemStorage("media/coverImages")
        filename = fs.save(myfile.name, myfile)  # saves the file to `media` folder
        fs.url(filename)  # gets the url
        cover_Pic.objects.create(coverImage=filename, user_id=request.user.id)
        User.objects.filter(id=request.user.id).update(coverImage=filename)
        return HttpResponse(filename)


class user_Setting(ListView,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    model = user_Detail
    template_name = 'Profile/setting.html'
    context_object_name = 'users_data'


class updateContactInfo(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def  get(self, request):
        fname = request.GET.get('fname', None)
        lname = request.GET.get('lname', None)
        phone = request.GET.get('phone', None)
        if fname and lname:
            obj = User.objects.get(id=request.user.id)
            obj.first_name = fname
            obj.last_name = lname
            obj.save()
            data = {
                'success': 'success'
            }
        if phone:
            if not user_Detail.objects.filter(user_id=request.user.id).exists():
                obj = user_Detail.objects.create(
                    phone = phone,
                    user_id = request.user.id
                )

                data = {
                    'success': 'success'
                }
            else:
                obj = user_Detail.objects.get(user_id=request.user.id)
                obj.phone = phone
                saved = obj.save()
                data = {
                    'success': 'success'
                    }
        return JsonResponse(data)

class updateAdditionalInfo(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def  get(self, request):
        gender = request.GET.get('gender', None)
        relationship = request.GET.get('relationship', None)
        dob = request.GET.get('dob')
        hometown = request.GET.get('hometown', None)
        city = request.GET.get('city', None)
        work_at = request.GET.get('workat', None)
        
        if not user_Detail.objects.filter(user_id=request.user.id).exists():
            obj = user_Detail.objects.create(
                relationship = relationship,
                hometown = hometown,
                lives_in = city,
                work_at = work_at,
                user_id = request.user.id
            )
            data = {
                'success': 'success'
                }
        else:
            obj = user_Detail.objects.get(user_id=request.user.id)
            if relationship:
                obj.relationship = relationship
            if hometown:
                obj.hometown = hometown
            if city:
                obj.lives_in = city
            if work_at:
                obj.work_at = work_at
            if dob:
                obj.dob = dob
            if gender:
                obj.gender = gender
            obj.save()
            data = {
                'success': 'success'
                }
        return JsonResponse(data)
class changePassword(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def  get(self, request):
        oldpassword = request.GET.get('oldpassword')
        newpassword = request.GET.get('newpassword')
        obj = User.objects.get(email=request.user.email)
        if obj.check_password(oldpassword):
            obj.set_password(newpassword)
            obj.save()
            update_session_auth_hash(request,obj)
            data = {
                    'message':'success'
                }
        else:
            data = {
                'message':'not-mached'
            }
        return JsonResponse(data)

class changeEmail(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def  get(self, request):
        newemail = request.GET.get('newemail')
        password = request.GET.get('password')
        obj = User.objects.get(email=request.user.email)
        if obj.check_password(password):
            obj.email = newemail
            obj.save()
            saved = User.objects.get(email=newemail)
            update_session_auth_hash(request,saved)
            data = {
                'message':'success'
            }
        else:
            data = {
                'message':'failed'
            }
        return JsonResponse(data)


class deleteAccount(RedirectView,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    url = reverse_lazy('user_accounts:login')
    def get(self, request, *args, **kwargs):
        delete_account = request.GET.get('delete_account')
        obj = User.objects.get(email=request.user.email)
        obj.is_active=False
        obj.save()
        auth.logout(request)
        return super(deleteAccount, self).get(request, *args, **kwargs)

class fetchPosts(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request,id):
        qs = Post.objects.filter(user_id=id).values('id','body','thumbnail','status','comment_enabled','created_at','updated_at','user__first_name','user__last_name','user__profileImage','user__gender','user__id').order_by('-id')
        posts = json.dumps(list(qs),indent=2,cls=MyEncoder)
        return HttpResponse(posts)

class allFiles(View,LoginRequiredMixin):
    login_url = '/user_accounts/login/'
    def get(self,request,id):
        current_url = request.path_info
        if 'photos' in current_url:
            data = Post.objects.filter(user_id = id).values('thumbnail')
            name = 'Photos'
        elif 'videos' in current_url:
            data = Post.objects.filter(user_id = id).values('thumbnail')
            name = 'Videos'
        elif 'profilepics' in current_url:
            data = profile_Pic.objects.filter(user_id = id).values('profileImage')
            name = 'Profile Pics'
        elif 'coverpics' in current_url:
            data = cover_Pic.objects.filter(user_id = id).values('coverImage')
            name = 'Cover Pics'
        return render(request,'Profile/gallery.html',{'data':data,'name':name})


@login_required(login_url=reverse_lazy("user_accounts:login"))
def checkFriendOrNot(request):
    user = request.GET.get('user')
    if Friend.objects.filter(Q(friend_id = user,user_id=request.user.id)|Q(user_id=user,friend_id=request.user.id)).exists():
        check = Friend.objects.get(Q(friend_id = user,user_id=request.user.id)|Q(user_id=user,friend_id=request.user.id))
        if check: 
            if check.status == 'requested':
                status={'requested':'requested',
                        'user_id':check.user_id,
                        'friend_id':check.friend_id}
            elif check.status == 'friend':
                status={'friend':'friend',
                        'user_id':check.user_id,
                        'friend_id':check.friend_id}
    else:
        status={'no':'no'}
    return JsonResponse(status)

@login_required(login_url=reverse_lazy("user_accounts:login"))
def removeProfilePic(request):
    update = User.objects.filter(id=request.user.id).update(profileImage=None)
    if update:
        return JsonResponse({'success':'success'})


@login_required(login_url=reverse_lazy("user_accounts:login"))
def removeCovePic(request):
    update = User.objects.filter(id=request.user.id).update(coverImage=None)
    if update:
        return JsonResponse({'success':'success'})