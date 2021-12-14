from rest_framework import permissions


class NotAuthenticated(permissions.BasePermission):
    """
    Non authenticated user only.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsStaffOrOwner(permissions.BasePermission):
    """
    Staff or Owner only
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow admins to edit an object.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff
