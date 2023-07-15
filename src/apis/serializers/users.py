from uuid import UUID

from users.models import User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from django.contrib.auth.models import Permission, Group


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields =('id', 'codename')


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')


class UserFullSerializer(serializers.ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'

        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'email', 'last_login', 'is_staff', 'is_active', 'date_joined',
            'username', 'enterprise', 'user_permissions', 'created_at', 'updated_at')


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'email', 'is_staff', 'password', 'is_active', 'username', 'enterprise', 'created_at', 'updated_at')


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'username', 'enterprise', 'created_at', 'updated_at')


class UpdatePasswordStaffSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={"input_type": "password"}, required=False, help_text='Not required if it is a staff or superadmin ')
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={"input_type": "password"}, required=True, help_text='Not required if it is a staff or superadmin ')
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_old_password(self, old_password: str) -> str:
        if (self.instance.is_superuser, self.instance.is_staff) == (False, False):
            # We need to control for non-superuser or non-staff
            if self.instance.check_password(old_password) is False:
                msg = _("Incorrect current Password")
                raise serializers.ValidationError(msg)

        return old_password

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance


class PermissionGrantRequest(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    user = serializers.UUIDField()

    def validate_permissions(self, permissions: list):
        if Permission.objects.filter(id__in=permissions).count() != len(permissions):
            msg = _("Some ID are not permissions IDs. Please check again")
            raise serializers.ValidationError(msg)

        return permissions

    def validate_user(self, user: UUID):
        if User.objects.filter(id=user).exists() is False:
            msg = _("User ID does not exist")
            raise serializers.ValidationError(msg)

        return user

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user'])
        permissions = Permission.objects.filter(id__in=validated_data['permissions'])

        for perm in permissions:
            user.user_permissions.add(perm)

        return user


class PermissionDenyRequest(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    user = serializers.UUIDField()

    def validate_permissions(self, permissions: list):
        if Permission.objects.filter(id__in=permissions).count() != len(permissions):
            msg = _("Some ID are not permissions IDs. Please check again")
            raise serializers.ValidationError(msg)

        return permissions

    def validate_user(self, user: UUID):
        if User.objects.filter(id=user).exists() is False:
            msg = _("User ID does not exist")
            raise serializers.ValidationError(msg)

        return user

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user'])
        permissions = Permission.objects.filter(id__in=validated_data['permissions'])

        # PS: it seems we can not remove permission with list on one time. We have to do it one by one
        for perm in permissions:
            user.user_permissions.remove(perm)

        return user


class GroupGrantRequest(serializers.Serializer):
    groups = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    user = serializers.UUIDField()

    def validate_groups(self, groups: list):
        if Group.objects.filter(id__in=groups).count() != len(groups):
            msg = _("Some IDs are not groups IDs. Please check again")
            raise serializers.ValidationError(msg)

        return groups

    def validate_user(self, user: UUID):
        if User.objects.filter(id=user).exists() is False:
            msg = _("User ID does not exist")
            raise serializers.ValidationError(msg)

        return user

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user'])
        groups = Group.objects.filter(id__in=validated_data['groups'])

        for group in groups:
            group.user_set.add(user)

        return user


class GroupDenyRequest(serializers.Serializer):
    groups = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    user = serializers.UUIDField()

    def validate_groups(self, groups: list):
        if Group.objects.filter(id__in=groups).count() != len(groups):
            msg = _("Some IDs are not groups IDs. Please check again")
            raise serializers.ValidationError(msg)

        return groups

    def validate_user(self, user: UUID):
        if User.objects.filter(id=user).exists() is False:
            msg = _("User ID does not exist")
            raise serializers.ValidationError(msg)

        return user

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['user'])
        groups = Group.objects.filter(id__in=validated_data['groups'])

        for group in groups:
            group.user_set.remove(user)

        return user
