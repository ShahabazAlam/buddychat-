from django.urls import path
from friends.views import *
app_name = "friends"

urlpatterns = [
    path('find-friends/', FindFriendsListView.as_view(), name="find-friends"),
    path('suggest-friends/', SuggestFriends.as_view(),name='suggest-friends'),
    path('friend-requests/',RequestList.as_view(), name='friend-requests'),
    path('send-request/<slug:id>', send_request, name="send-request"),
    path('accept-request/<slug:id>', accept_request, name="accept-request"),
    path('cancel-request/<slug:id>', Cancel_Request, name="cancel-request"),
    path('your-friends/', yourFriends.as_view(), name="your-friends"),
    path('unfriend/<slug:id>', Unfriend, name="your-friends"),
    path('block_user/<slug:id>', BlockUser, name="your-friends"),
    path('friend_friends/<slug:id>', getFriendFriendList, name="getFriendFriendList"),
    path('see_all/<slug:id>', loadAllFriend, name="loadAllFriend"),
    path('blocked-users/', loadBlockedUsers, name="loadBlockedUsers"),
    path('unblock/<slug:id>', unblockUsers, name="unblockUsers"),

]
