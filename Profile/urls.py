from django.urls import path
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from Profile.views import *
app_name = "Profile"
pattern_name = "Profile"

urlpatterns = [
    path('user_timeline/<slug:id>', user_Timeline.as_view(), name="find-friends"),
    path('save_cover_pic/', cover_Pic_Save, name="save_profile_pic"),
    path('save_profile_pic/', profile_Pic_Save, name="save_cover_pic"),
    path('setting/', user_Setting.as_view(), name="setting"),
    path('update-contact-info/', updateContactInfo.as_view(), name="updateContactInfo"),
    path('update-additional-info/', updateAdditionalInfo.as_view(), name="updateContactInfo"),
    path('change-password/', changePassword.as_view(), name="changePassword"),
    path('change-email/', changeEmail.as_view(), name="changeEmail"),
    path('delete-account/', deleteAccount.as_view(), name="deleteAccount"),
    path('fetch-posts/<slug:id>', fetchPosts.as_view(), name="deleteAccount"),
    path('all-photos/<slug:id>', allFiles.as_view(), name="deleteAccount"),
    path('all-videos/<slug:id>', allFiles.as_view(), name="deleteAccount"),
    path('all-profilepics/<slug:id>', allFiles.as_view(), name="deleteAccount"),
    path('all-coverpics/<slug:id>', allFiles.as_view(), name="deleteAccount"),
    path('check-friend-or-not/', checkFriendOrNot, name="checkFriendOrNot"),
    path('remove-profile-pic/', removeProfilePic, name="removeProfilePic"),
    path('remove-cover-pic/', removeCovePic, name="removeCovePic"),

    
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)