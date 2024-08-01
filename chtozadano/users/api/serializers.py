from rest_framework import serializers

from users.models import BecomeAdmin


class BecomeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = BecomeAdmin
        fields = "__all__"
