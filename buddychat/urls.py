from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user_accounts/',include('user_accounts.urls')),
    path('',include('buddyapp.urls')),
    path('friends/',include('friends.urls')),
    path('profile/',include('Profile.urls')),
    path('newsfeeds/',include('newsfeeds.urls')),
    path('messages/', include('communications.urls')),
    path('notifications/', include('notifications.urls')),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)