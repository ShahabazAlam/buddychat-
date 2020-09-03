from django.urls import path
from .views import *

app_name = "communications"

urlpatterns = [
    path('', all_messages, name="all-messages"),
    path('<int:id>/', one_to_one_chat, name="one_to_one_chat"),
    path('friendlist/<int:id>/', friendList, name="friendList"),
    path('check-online/', checkOnline, name="checkOnline"),
    path('delete-message/', deleteMessage, name="deleteMessage"),
    path('read-msg-notifications/', readMsgNotifications, name="readMsgNotifications"),
    path('remove-all-notifications/', removeAllNotifications, name="removeAllNotifications"),
    path('last-message/',lastMessage, name="lastMessage"),
    path('delete-converstion/',delectConversation, name="delectConversation"),
]
