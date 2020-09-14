from rest_framework import permissions
from rest_framework.request import Request

from ddl.settings import JUDGE_TOKEN


class JudgePermission(permissions.BasePermission):

    def has_permission(self, request: Request, view):
        return request.headers.get('JudgeToken', None) == JUDGE_TOKEN
