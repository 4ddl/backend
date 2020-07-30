from rest_framework import serializers
import re
from django.contrib import auth
from user.models import User, Activity
from django.core.exceptions import ObjectDoesNotExist
from user.utils import USERNAME_PATTERN, PASSWORD_PATTERN
from django.utils import timezone


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_admin']
        read_only_fields = ['username', 'email', 'is_admin']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    captcha = serializers.CharField()

    @staticmethod
    def validate_username(value):
        if re.match(USERNAME_PATTERN, value) is None:
            raise serializers.ValidationError(
                'Username can only contain letters, numbers, -, _ and no shorter than 6 and no longer than 20')
        return value

    @staticmethod
    def validate_password(value):
        if re.match(PASSWORD_PATTERN, value) is None:
            raise serializers.ValidationError(
                'Password can only contain letters, numbers, -, _ and no shorter than 8 and no longer than 20')
        return value

    def validate(self, data):
        user = auth.authenticate(username=data['username'],
                                 password=data['password'])
        if not user:
            raise serializers.ValidationError('Username or password wrong')
        return data

    def login(self, request):
        user = auth.authenticate(username=self.validated_data['username'],
                                 password=self.validated_data['password'])
        auth.login(request, user)
        user.last_login = timezone.now()
        user.save()
        Activity.objects.create(user=user, category=Activity.USER_LOGIN, info='登录成功')
        return user


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()
    captcha = serializers.CharField()

    def save(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']
        username = self.validated_data['username']
        user = User.objects.create_user(username=username, password=password, email=email)
        Activity.objects.create(user=user, category=Activity.USER_REGISTER, info='注册成功')
        user.save()

    @staticmethod
    def validate_username(value):
        if re.match(USERNAME_PATTERN, value) is None:
            raise serializers.ValidationError(
                'Username can only contain letters, numbers, -, _ and no shorter than 6 and no longer than 20')
        try:
            User.objects.get(username=value)
            raise serializers.ValidationError('Username exist')
        except ObjectDoesNotExist:
            pass
        return value

    @staticmethod
    def validate_password(value):
        if re.match(PASSWORD_PATTERN, value) is None:
            raise serializers.ValidationError(
                'Password can only contain letters, numbers, -, _ and no shorter than 8 and no longer than 20')
        return value

    @staticmethod
    def validate_email(value):
        if len(value) > 100:
            raise serializers.ValidationError('Email address is too long')
        try:
            User.objects.get(email=value)
            raise serializers.ValidationError('Email address occupied')
        except ObjectDoesNotExist:
            pass
        return value
