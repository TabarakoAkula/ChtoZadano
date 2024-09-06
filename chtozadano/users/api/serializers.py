from django.contrib.auth.models import User as DefaultUser
from rest_framework import serializers

from users.models import BecomeAdmin, User


class BecomeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = BecomeAdmin
        fields = "__all__"


class DefaultUserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultUser
        fields = (
            "first_name",
            "last_name",
        )


class UserSerializer(serializers.ModelSerializer):
    user = DefaultUserNameSerializer()

    class Meta:
        model = User
        fields = (
            "telegram_id",
            "group",
            "user",
        )


class UserNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
