from django.contrib import auth
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.views import Response

from user.serializers import UserInfoSerializer, LoginSerializer, RegisterSerializer
from utils import msg
from utils.views import CaptchaAPI


class AuthAPI(APIView):
    # 查询登录状态和登录信息
    @staticmethod
    def get(request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(msg(UserInfoSerializer(request.user).data))
        else:
            return Response(msg(err='not login'))

    # 登录
    @staticmethod
    def post(request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(msg(err='please sign out first before try to login'))
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            if not CaptchaAPI.verify_captcha(request, serializer.validated_data['captcha']):
                return Response(msg(err='captcha verify error'))
            user = serializer.login(request)
            if user:
                return Response(msg(UserInfoSerializer(user).data))
        return Response(msg(err=serializer.errors))

    # 注册
    @staticmethod
    def put(request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(msg(err='please sign out first before try to register'))
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            if not CaptchaAPI.verify_captcha(request, serializer.validated_data['captcha']):
                return Response(msg(err='captcha verify error'))
            serializer.save()
            return Response(msg('success'))
        return Response(msg(err=serializer.errors))

    # 退出登陆
    @staticmethod
    def delete(request, *args, **kwargs):
        auth.logout(request)
        return Response(msg('success'))
