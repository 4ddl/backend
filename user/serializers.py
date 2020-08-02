import re
import uuid

from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from user.models import User, Activity
from user.utils import USERNAME_PATTERN, PASSWORD_PATTERN


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['username']


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
        if user.is_active:
            auth.login(request, user)
            user.save()
            Activity.objects.create(user=user, category=Activity.USER_LOGIN, info='登录成功')
            return user, None
        else:
            return None, 'User not activated, please check your activated email'


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()
    captcha = serializers.CharField()

    def save(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']
        username = self.validated_data['username']

        user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email,
                                        is_active=False,
                                        activated_code=uuid.uuid4())
        Activity.objects.create(user=user, category=Activity.USER_REGISTER, info='Register success')
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
