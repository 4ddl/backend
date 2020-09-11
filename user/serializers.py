import random
import re

from django.contrib import auth
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import serializers
from django.utils.translation import gettext as _
from ddl.settings import ACTIVATE_CODE_AGE
from user.models import User, Activity, StudentInfo
from user.utils import USERNAME_PATTERN, PASSWORD_PATTERN
from utils.mail import send_activated_email
from uuid import uuid4
from utils.views import CaptchaAPI


class StudentInfoShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        fields = ['id', 'school']


class PermissionListField(serializers.RelatedField):
    def to_representation(self, value: Permission):
        return {
            'id': value.id,
            'name': f'{value.content_type.app_label}.{value.codename}'
        }


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['username']


class AdvancedUserInfoSerializer(serializers.ModelSerializer):
    user_permissions = PermissionListField(read_only=True, many=True)
    username = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'is_superuser',
            'total_passed',
            'total_accepted',
            'total_submitted',
            'activated',
            'ban',
            'user_permissions']


class UserInfoSerializer(serializers.ModelSerializer):
    user_permissions = PermissionListField(read_only=True, many=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'is_superuser',
            'total_passed',
            'total_accepted',
            'total_submitted',
            'activated',
            'user_permissions']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    captcha = serializers.CharField()

    def validate_captcha(self, value):
        request = self.context['request']
        if not CaptchaAPI.verify_captcha(request, value):
            raise serializers.ValidationError(_('Captcha verify error.'))
        return value

    @staticmethod
    def validate_username(value):
        if re.match(USERNAME_PATTERN, value) is None:
            raise serializers.ValidationError(
                _('Username can only contain letters, numbers, -, _ and no shorter than 6 and no longer than 20'))
        return value

    @staticmethod
    def validate_password(value):
        if re.match(PASSWORD_PATTERN, value) is None:
            raise serializers.ValidationError(
                _('Password can only contain letters, numbers, -, _ and no shorter than 8 and no longer than 20'))
        return value

    def validate(self, data):
        user = auth.authenticate(username=data['username'],
                                 password=data['password'])
        if not user:
            raise serializers.ValidationError(_('Username or password wrong'))
        return data

    def login(self, request):
        user = auth.authenticate(username=self.validated_data['username'],
                                 password=self.validated_data['password'])
        if user.activated:
            auth.login(request, user)
            user.save()
            Activity.objects.create(user=user, category=Activity.USER_LOGIN, info='登录成功')
            return user, None
        elif user.ban:
            return None, _('You have been banned from this website.')
        else:
            user.activate_uuid = uuid4()
            user.save()
            activate_code = '%06d' % random.randint(0, 999999)
            send_activated_email(user.username,
                                 user.email,
                                 activate_code)
            cache.set(f'activate-code-{user.activate_uuid}', activate_code, ACTIVATE_CODE_AGE)
            return user, _('Account not activated, '
                           'an mail has been sent to your email address, '
                           'please check your mail box')


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()
    captcha = serializers.CharField()

    def validate_captcha(self, value):
        request = self.context['request']
        if not CaptchaAPI.verify_captcha(request, value):
            raise serializers.ValidationError(_('Captcha verify error.'))
        return value

    def save(self, **kwargs):
        email = self.validated_data['email']
        password = self.validated_data['password']
        username = self.validated_data['username']

        user = User.objects.create_user(username=username,
                                        password=password,
                                        email=email)
        Activity.objects.create(user=user, category=Activity.USER_REGISTER, info='注册成功')
        user.save()
        activate_code = '%06d' % random.randint(0, 999999)
        send_activated_email(user.username,
                             user.email,
                             activate_code)
        cache.set(f'activate-code-{user.activate_uuid}', activate_code, ACTIVATE_CODE_AGE)
        return user

    @staticmethod
    def validate_username(value):
        if re.match(USERNAME_PATTERN, value) is None:
            raise serializers.ValidationError(
                _('Username can only contain letters, numbers, -, _ and no shorter than 6 and no longer than 20'))
        try:
            User.objects.get(username=value)
            raise serializers.ValidationError(_('Username exist'))
        except ObjectDoesNotExist:
            pass
        return value

    @staticmethod
    def validate_password(value):
        if re.match(PASSWORD_PATTERN, value) is None:
            raise serializers.ValidationError(
                _('Password can only contain letters, numbers, -, _ and no shorter than 8 and no longer than 20'))
        return value

    @staticmethod
    def validate_email(value):
        if len(value) > 100:
            raise serializers.ValidationError(_('Email address is too long'))
        try:
            User.objects.get(email=value)
            raise serializers.ValidationError(_('Email address occupied'))
        except ObjectDoesNotExist:
            pass
        return value


class ActivateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)
    id = serializers.IntegerField()

    def validate_code(self, value):
        if str(value).isdigit():
            return value
        raise serializers.ValidationError(_('Activate code error'))

    def active(self):
        try:
            user = User.objects.get(id=self.validated_data['id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('User not exist.'))
        if user.activated:
            raise serializers.ValidationError(_('User activated.'))

        saved_code = cache.get(f'activate-code-{user.activate_uuid}')
        if saved_code is None:
            activate_code = '%06d' % random.randint(0, 999999)
            send_activated_email(user.username,
                                 user.email,
                                 activate_code)
            cache.set(f'activate-code-{user.activate_uuid}', activate_code, ACTIVATE_CODE_AGE)
            raise serializers.ValidationError(_('Activate code expired, server send email again.'))
        elif saved_code != self.validated_data['code']:
            raise serializers.ValidationError(_('Activate code error'))
        user.activated = True
        user.save()
        cache.delete(f'activate-code-{user.activate_uuid}')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    @staticmethod
    def validate_new_password(value):
        if re.match(PASSWORD_PATTERN, value) is None:
            raise serializers.ValidationError(
                _('Password can only contain letters, numbers, -, _ and no shorter than 8 and no longer than 20'))
        return value

    def validate_old_password(self, old):
        user = self.context['user']
        if not auth.authenticate(username=user.username,
                                 password=old):
            raise serializers.ValidationError(_('Old password error'))
        return old

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError(_('The new password cannot be the same as the old password'))
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()


class ActivityListSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()

    class Meta:
        model = Activity
        fields = ['id', 'user', 'info', 'category', 'info', 'create_time']


class RankSerializer(serializers.ModelSerializer):
    student = StudentInfoShortSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'total_passed',
                  'total_accepted',
                  'total_submitted',
                  'student']


class FollowingSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    follow = serializers.BooleanField()

    @staticmethod
    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_('User not exist.'))
        return value


class POSTCheckEmailAddressSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField()

    def validate_captcha(self, value):
        request = self.context['request']
        if not CaptchaAPI.verify_captcha(request, value):
            raise serializers.ValidationError(_('Captcha verify error.'))
        return value

    @staticmethod
    def validate_email(value):
        if len(value) > 100:
            raise serializers.ValidationError(_('Email address is too long'))
        try:
            User.objects.get(email=value)
            raise serializers.ValidationError(_('Email address occupied'))
        except ObjectDoesNotExist:
            pass
        return value

    def save(self, user: User):
        user.activate_uuid = uuid4()
        user.save()
        activate_code = '%06d' % random.randint(0, 999999)
        send_activated_email(user.username,
                             self.validated_data['email'],
                             activate_code)
        cache.set(f'update-mail-code-{user.activate_uuid}', activate_code, ACTIVATE_CODE_AGE)
        cache.set(f'update-mail-address-{user.activate_uuid}', self.validated_data['email'], ACTIVATE_CODE_AGE)


class PUTChangeEmailAddressSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_code(self, value):
        user = self.context['user']
        if cache.get(f'update-mail-code-{user.activate_uuid}') == value:
            return value
        raise serializers.ValidationError(_('Verify code error'))

    def save(self, **kwargs):
        user = self.context['user']
        email = cache.get(f'update-mail-address-{user.activate_uuid}')
        if email:
            try:
                user.email = email
                user.save()
                cache.delete(f'update-mail-address-{user.activate_uuid}')
                cache.delete(f'update-mail-code-{user.activate_uuid}')
            except IntegrityError:
                raise serializers.ValidationError(_('email address occupied, please change another.'))
        else:
            raise serializers.ValidationError(_('Please send check email address again.'))


class StudentInfoSerializer(serializers.ModelSerializer):
    school = serializers.ChoiceField(choices=StudentInfo.SCHOOL_CHOICES)

    def save(self, user: User):
        try:
            user.student.school = self.validated_data['school']
            user.student.student_id = self.validated_data['student_id']
            user.student.save()
        except StudentInfo.DoesNotExist:
            StudentInfo(user=user, school=self.validated_data['school'],
                        student_id=self.validated_data['student_id']).save()

    class Meta:
        model = StudentInfo
        fields = ['school', 'student_id']
