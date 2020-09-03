from django.urls import path
from .views import *

app_name = "notifications"

urlpatterns = [
    path('mark-all-notifications-as-read', mark_all_notifications_as_read, name="mark-all-notifications-as-read"),
    path('mark-notification-as-read', mark_notification_as_read, name="mark-notifications-as-read"),
    path('read-one-comment/<slug:post_id>/<slug:cl_id>', readOneComment, name="readOneComment"),
    path('read-comment/',readComment,name="readComment"),
    path('read-birthday-notifications/',readBirthdayNotification, name="readBirthdayNotification"),
]
