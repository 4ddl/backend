from rest_framework.permissions import BasePermission, SAFE_METHODS


class IfAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if view.perms is None:
            return True
        if type(view.perms) != list:
            return False
        if request.user.is_anonymous:
            return False
        return request.user.is_admin_or_has_perms(view.perms)
