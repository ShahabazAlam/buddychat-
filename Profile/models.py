from django.db import models
from user_accounts.models import User
from datetime import date
import datetime

# Create your models here.
class profile_Pic(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	profileImage = models.ImageField(upload_to='media/',null=True,blank=True)
	created_at=models.DateTimeField(default=datetime.datetime.now)
	updated_at=models.DateTimeField(default=datetime.datetime.now)

	class Meta:
		db_table = 'profile_Pic'

class cover_Pic(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	coverImage = models.ImageField(upload_to='media/',null=True,blank=True)
	created_at=models.DateTimeField(default=datetime.datetime.now)
	updated_at=models.DateTimeField(default=datetime.datetime.now)

	class Meta:
		db_table = 'cover_Pic'

class user_Detail(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    dob = models.DateField(max_length=15,null=True,blank=True)
    phone = models.CharField(max_length=12,blank=True,null=True)
    lives_in =models.CharField(max_length=80,blank=True,null=True)
    hometown = models.CharField(max_length=80,blank=True,null=True)
    relationship = models.CharField(max_length=50,blank=True,null=True)
    work_at = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        db_table = 'user_Detail'

