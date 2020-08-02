import random
import re

from django.contrib import auth
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ddl.settings import ACTIVATE_CODE_AGE
from user.models import User, Activity
from user.utils import USERNAME_PATTERN, PASSWORD_PATTERN
from utils.mail import send_activated_email


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
        if user.activated:
            auth.login(request, user)
            user.save()
            Activity.objects.create(user=user, category=Activity.USER_LOGIN, info='登录成功')
            return user
        else:
            activate_code = '%6d' % random.randint(0, 999999)
            send_activated_email(user.username,
                                 user.email,
                                 activate_code)
            cache.set(f'activate-code-{user.id}', activate_code, ACTIVATE_CODE_AGE)
            raise serializers.ValidationError('Account not activated, '
                                              'an mail has send to your email address, '
                                              'please check your mail box')


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
                                        email=email)
        Activity.objects.create(user=user, category=Activity.USER_REGISTER, info='Register success')
        user.save()
        activate_code = '%6d' % random.randint(0, 999999)
        send_activated_email(user.username,
                             user.email,
                             activate_code)
        cache.set(f'activate-code-{user.id}', activate_code, ACTIVATE_CODE_AGE)
        return user

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


class ActivateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_code(self, value):
        if str(value).isdigit():
            return value
        raise serializers.ValidationError('Activate code error')

    def active(self, user):
        if cache.get(f'activate-code-{user.id}') != self.validated_data['code']:
            raise serializers.ValidationError('Activate code error')
