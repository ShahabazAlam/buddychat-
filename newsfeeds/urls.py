from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import *

urlpatterns = [
    path('post/',savePost,name="savePost"),
    path('fetch-posts/',fetchPosts.as_view(),name="fetchPosts"),
    path('addComment/',addComment.as_view(),name="addComment"),
    path('fetch-gallery-images/',fetchGalleryImages.as_view(),name="fetchGalleryImages"),
    path('like-post/',likePost.as_view(),name="likePost"),
    path('noc-like-comment/',nocLikeComment.as_view(),name="nocLikeComment"),
    path('check-like/',checkLike.as_view(),name="checkLike"),
    path('disable-comment/',disableComment.as_view(),name="disableComment"),
    path('check-enabledisable-comment/',checkEnableDisableComment.as_view(),name="disableComment"),
    path('delete-post/',deletePost.as_view(),name="deletePost"),
    path('updata-post/',updatePost.as_view(),name="updatePost"),
    path('delete-comments/',deleteComment.as_view(),name="deleteComment"),
    path('update-comment/',updateComment.as_view(),name="updateComment"),
    path('like-comment/',likeComment.as_view(),name="likeComment"),
    path('check-comment-like/',checkCommentLike.as_view(),name="checkCommentLike"),
    path('get-friend-name/',getName,name="getName"),
    path('save-status/',saveStatus,name="saveStatus"),
    path('delete-status/',deleteStatus,name="deleteStatus"),    
    path('search/',searchData,name="search"),
    
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)