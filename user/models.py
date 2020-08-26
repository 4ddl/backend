from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from submission.config import Verdict


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, password, is_superuser=False, activated=False):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), username=username)
        user.is_superuser = is_superuser
        user.activated = activated
        user.activate_uuid = uuid4()
        user.set_password(password)
        user.save(using=self._db)
        Activity(
            user=user,
            info='注册管理员账号' if user.is_superuser else '注册用户账号'
        ).save()
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password, is_superuser=True, activated=True)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, null=False, blank=False, unique=True)
    password = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    ban = models.BooleanField(default=False, null=False, blank=False)
    activated = models.BooleanField(default=False, null=False, blank=False)
    activate_uuid = models.UUIDField(null=False, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    last_login = models.DateTimeField(blank=True, null=True, editable=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    # 通过的题目数量
    @property
    def total_passed(self):
        return self.submissions.filter(verdict=Verdict.ACCEPTED).values('problem_id').distinct().count()

    # 提交的AC的结果的数量
    @property
    def total_accepted(self):
        return self.submissions.filter(verdict=Verdict.ACCEPTED).count()

    # 提交的数量
    @property
    def total_submitted(self):
        return self.submissions.count()

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_active(self):
        return True

    @property
    def last_submit_time(self):
        if self.submissions.count() > 0:
            return self.submissions.all().order_by('-id')[0].create_time
        else:
            return None

    def __str__(self):
        return str(self.username)

    class Meta:
        permissions = [('manage_privilege', 'Manage User Privilege')]


class Activity(models.Model):
    USER_LOGIN = 'UL'
    USER_REGISTER = 'UR'
    CATEGORY_CHOICES = [
        (USER_LOGIN, 'User Login'),
        (USER_REGISTER, 'User Register')
    ]
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    info = models.CharField(max_length=200)
    create_time = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=4, choices=CATEGORY_CHOICES, null=True, blank=True)

    def __str__(self):
        return f'{self.id}-{self.user}-{self.category}'

    class Meta:
        verbose_name_plural = 'Activities'
