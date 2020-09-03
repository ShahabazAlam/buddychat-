from django.db import models
from user_accounts.models import User
import datetime
from django.conf import settings

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post")
    body = models.TextField(null=True,blank=True)
    thumbnail = models.FileField(null=True)
    status = models.CharField(max_length=20,null=True,blank=True)
    comment_enabled = models.CharField(max_length=20, default='enabled')
    page = models.CharField(max_length=20)
    created_at=models.DateTimeField(default=datetime.datetime.now)
    updated_at=models.DateTimeField(default=datetime.datetime.now)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    content = models.TextField(null=True,blank=True)
    comment_image = models.ImageField(null=True,blank=True)
    created_at=models.DateTimeField(default=datetime.datetime.now)
    updated_at=models.DateTimeField(default=datetime.datetime.now)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like')
    created_at=models.DateTimeField(default=datetime.datetime.now)
    updated_at=models.DateTimeField(default=datetime.datetime.now)

class Gallery(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='gallery')
    images = models.FileField(null=True,blank=True)
    created_at=models.DateTimeField(default=datetime.datetime.now)
    updated_at=models.DateTimeField(default=datetime.datetime.now)

class commentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="commentlike")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userlike')
    created_at=models.DateTimeField(default=datetime.datetime.now)
    updated_at=models.DateTimeField(default=datetime.datetime.now)

class Status(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='user_status')
    image = models.FileField(null=True,blank=True)
    created_at=models.DateTimeField(default=datetime.datetime.now)
    expiration_date = models.DateTimeField()