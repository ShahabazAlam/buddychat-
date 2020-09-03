from rest_framework import serializers

from user_accounts.models import User
from notifications.models import commentLikeNotifications
from .models import Status


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)


class postNotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = commentLikeNotifications
        fields = "__all__"
