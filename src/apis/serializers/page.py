import re

from docs.models import Page
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .part import PartResponseSerializer
from .users import PermissionSerializer


class PageRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ('permission',)

    def validate_name(self, name: str) -> str:
        if name is not None:
            if bool(re.match("^[A-Za-z0-9 ]+$", name)) is False:
                msg = _("Name can not contains special characters")
                raise serializers.ValidationError(msg)

        return name


class PageResponseSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(many=False, read_only=True)

    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ('permission',)

    def validate_name(self, name: str) -> str:
        if name is not None:
            if bool(re.match("^[A-Za-z0-9 ]+$", name)) is False:
                msg = _("Name can not contains special characters")
                raise serializers.ValidationError(msg)

        return name


class PageWithPartSerializer(serializers.ModelSerializer):
    parts = PartResponseSerializer(many=True, read_only=True)
    permission = PermissionSerializer(many=False, read_only=True)

    class Meta:
        model = Page
        fields = (
            'id', 'name', 'description', 'version', 'is_under_maintenance', 'parts', 'permission',
            'created_at', 'updated_at'
        )
        read_only_fields = ('permission',)

    def validate_name(self, name: str) -> str:
        if name is not None:
            if bool(re.match("^[A-Za-z0-9 ]+$", name)) is False:
                msg = _("Name can not contains special characters")
                raise serializers.ValidationError(msg)

        return name
