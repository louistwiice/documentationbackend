import re

from docs.models import Version
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .users import PermissionSerializer


class VersionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'
        read_only_fields = ('permission',)

    def validate_name(self, name: str) -> str:
        if name is not None:
            if bool(re.match("^[A-Za-z0-9]+$", name)) is False:
                msg = _("Name can not contains special characters or space")
                raise serializers.ValidationError(msg)

        return name


class VersionResponseSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(many=False, read_only=True)

    class Meta:
        model = Version
        fields = '__all__'
        read_only_fields = ('permission',)

    def validate_name(self, name: str) -> str:
        if name is not None:
            if bool(re.match("^[A-Za-z0-9]+$", name)) is False:
                msg = _("Name can not contains special characters or space")
                raise serializers.ValidationError(msg)

        return name

