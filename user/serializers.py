from rest_framework import serializers
import re
from django.contrib import auth
from user.models import User
from django.core.exceptions import ObjectDoesNotExist
from user.utils import USERNAME_PATTERN, PASSWORD_PATTERN


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_admin']
        read_only_fields = ['username', 'email', 'is_admin']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

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

    def login(self, request):
        user = auth.authenticate(username=self.validated_data['username'],
                                 password=self.validated_data['password'])
        if user:
            if request:
                auth.login(request, user)
            return user
        raise serializers.ValidationError(
            'Username or password wrong')


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()

    def save(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']
        username = self.validated_data['username']
        user = User.objects.create_user(username=username, password=password, email=email)
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
