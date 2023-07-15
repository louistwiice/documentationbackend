from rest_framework import permissions


class IsStaffOrAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(
            (request.user.is_superuser or request.user.is_staff) and request.user.is_authenticated
        )
