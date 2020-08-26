from rest_framework import permissions


class ManageProblemPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.user.has_perms('problem.manage_problem')
