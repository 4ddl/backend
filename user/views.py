from django.contrib import auth
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.views import Response
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request

from user.serializers import UserInfoSerializer, LoginSerializer, RegisterSerializer, ActivateSerializer, \
    ChangePasswordSerializer
from user.models import User
from utils.response import msg
from utils.views import CaptchaAPI


class AuthViewSet(ViewSet):
    # 查询登录状态和登录信息
    @action(methods=['GET'], detail=False)
    def info(self, request):
        if request.user.is_authenticated:
            return Response(msg(UserInfoSerializer(request.user).data))
        else:
            return Response(msg(err='Not login.'))

    # 登录
    @action(methods=['POST'], detail=False)
    def login(self, request):
        if request.user.is_authenticated:
            return Response(msg(err='Please sign out first before try to login.'))
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            if not CaptchaAPI.verify_captcha(request, serializer.validated_data['captcha']):
                return Response(msg(err='Captcha verify error.'))
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
            return Response(msg(err='Please sign out first before try to register.'))
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            if not CaptchaAPI.verify_captcha(request, serializer.validated_data['captcha']):
                return Response(msg(err='Captcha verify error.'))
            user = serializer.save()
            return Response(msg(UserInfoSerializer(user).data))
        return Response(msg(err=serializer.errors))

    # 退出登陆
    @action(methods=['DELETE'], detail=False)
    def logout(self, request):
        auth.logout(request)
        return Response(msg('Successful logout.'))

    @action(methods=['POST'], detail=False)
    def activate(self, request):
        serializer = ActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.active()
        return Response(msg('Successful activate.'))

    def user_info(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        return Response(msg(UserInfoSerializer(user).data))

    @action(methods=['PUT'], detail=False)
    def password(self, request: Request):
        if request.user.is_authenticated:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            auth.logout(request)
            return Response(msg('Success'))
        return Response(msg(err='Not login.'))


