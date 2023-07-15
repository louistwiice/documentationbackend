from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from apis.serializers.users import UserAuthSerializer
from users.models import User


class AuthenticationRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(label=_("identifier"), required=True, help_text="Username or Email")
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}, required=True
    )

    def validate_identifier(self, identifier: str) -> str:
        user = User.objects.filter(
            Q(username=identifier) | Q(email=identifier)
        )
        if user.exists() is False:
            msg = _("User Identifier (Email/Username) not found")
            raise serializers.ValidationError(msg)

        user = user.first()
        if not user.is_active:
            msg = _("User account is disabled.")
            raise serializers.ValidationError(msg, code="authorization")

        return identifier

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        user = authenticate(identifier=identifier, password=password)
        if user is None:
            msg = _("Unable to log in with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class AuthenticationResponseSerializer(serializers.Serializer):
    user = UserAuthSerializer(many=False, read_only=True, help_text="Connected User Information")
    access = serializers.CharField(help_text='Access Token')
    refresh = serializers.CharField(help_text='Refresh Token')
    token_type = serializers.CharField(help_text='Token Type')
    access_expired_in = serializers.IntegerField(help_text='Access Token expired time in second')
    refresh_expired_in = serializers.IntegerField(help_text='Access Token expired time in Days')


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
