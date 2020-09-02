from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.request import Request
from rest_framework.views import Response

from user.models import User
from user.perm import ManageUserPermission
from user.serializers import UserInfoSerializer, LoginSerializer, RegisterSerializer, ActivateSerializer, \
    ChangePasswordSerializer, ActivityListSerializer, AdvancedUserInfoSerializer, RankSerializer
from utils.response import msg
from utils.views import CaptchaAPI
from utils.tools import random_str


class AdvancedUserViewSet(viewsets.GenericViewSet,
                          UpdateModelMixin,
                          ListModelMixin,
                          RetrieveModelMixin):
    serializer_class = AdvancedUserInfoSerializer
    permission_classes = [ManageUserPermission]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(msg(serializer.data))

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(msg(serializer.data))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(msg(serializer.data))

    @action(methods=['POST'], detail=True)
    def reset_password(self, request, pk=None, *args, **kwargs):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        new_password = random_str(8)
        user.set_password(new_password)
        user.save()
        return Response(msg({
            'new_password': new_password
        }))


class AuthViewSet(viewsets.GenericViewSet, ListModelMixin):
    serializer_class = RankSerializer
    queryset = User.objects.all()

    # 查询登录状态和登录信息
    @action(methods=['GET'], detail=False)
    def info(self, request):
        if request.user.is_authenticated:
            return Response(msg(UserInfoSerializer(request.user).data))
        else:
            return Response(msg(err=_('Not login.')))

    # 登录
    @action(methods=['POST'], detail=False)
    def login(self, request):
        if request.user.is_authenticated:
            return Response(msg(err=_('Please sign out first before try to login.')))
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            if not CaptchaAPI.verify_captcha(request, serializer.validated_data['captcha']):
                return Response(msg(err=_('Captcha verify error.')))
            user, err = serializer.login(request)
            if user:
                return Response(msg(UserInfoSerializer(user).data, err=err))
            else:
                return Response(msg(err=err))
        return Response(msg(err=serializer.errors))

    # 注册
    @action(methods=['PUT'], detail=False)
    def register(self, request):
        if request.user.is_authenticated:
            return Response(msg(err=_('Please sign out first before try to register.')))
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            if not CaptchaAPI.verify_captcha(request, serializer.validated_data['captcha']):
                return Response(msg(err=_('Captcha verify error.')))
            user = serializer.save()
            return Response(msg(UserInfoSerializer(user).data))
        return Response(msg(err=serializer.errors))

    # 退出登陆
    @action(methods=['DELETE'], detail=False)
    def logout(self, request):
        auth.logout(request)
        return Response(msg(_('Successful logout.')))

    # 激活账号
    @action(methods=['POST'], detail=False)
    def activate(self, request):
        serializer = ActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.active()
        return Response(msg(_('Successful activate.')))

    # 获取个人信息
    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        return Response(msg(UserInfoSerializer(user).data))

    # 修改密码
    @action(methods=['PUT'], detail=False)
    def password(self, request: Request):
        if request.user.is_authenticated:
            serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            auth.logout(request)
            return Response(msg(_('Success')))
        raise NotAuthenticated

    # 获取活动记录
    @action(methods=['GET'], detail=True)
    def activities(self, request: Request, pk=None, *args, **kwargs):
        if request.user.is_authenticated and request.user.id == pk or request.user.is_staff:
            user = get_object_or_404(User.objects.all(), pk=pk)
            serializer = ActivityListSerializer(user.activities.all()[:10], many=True)
            return Response(msg(serializer.data))
        raise PermissionDenied

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = sorted(queryset, key=lambda x: (-x.total_passed, x.total_submitted, x.id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(msg(serializer.data))
