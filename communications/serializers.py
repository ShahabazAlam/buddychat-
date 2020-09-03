from rest_framework import serializers

from user_accounts.models import User
from notifications.models import MessageNotification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)


class MessageNotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = MessageNotification
        fields = "__all__"