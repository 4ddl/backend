from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from user import Perms


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, password, is_active=True, activate_code=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), username=username)
        user.is_active = is_active
        user.activated_code = activate_code
        user.set_password(password)
        user.save(using=self._db)
        Activity(user=user, info='register new account').save()
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.save(using=self._db)
        Activity(user=user, info='grant administrators privilege').save()
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, null=False, blank=False, unique=True)
    password = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    ban = models.BooleanField(default=False, null=False, blank=False)
    is_active = models.BooleanField(default=True, null=False, blank=False)
    activated_code = models.CharField(max_length=40, null=True, blank=True, default=None)
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    last_login = models.DateTimeField(blank=True, null=True, editable=False)
    is_admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True
        return False

    def has_module_perms(self, app_label):
        return True

    def is_admin_or_has_perm(self, perm: str):
        if self.is_admin:
            return True
        return len(self.perms.filter(perm=perm)) > 0

    def is_admin_or_has_perms(self, perms: list):
        if self.is_admin:
            return True
        return len(self.perms.all()) >= len(perms)

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return str(self.username)


class UserPerm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='perms')
    perm = models.CharField(max_length=6, choices=Perms.PERM_CHOICES, null=False, blank=False)

    class Meta:
        unique_together = (
            ('user', 'perm')
        )

    def __str__(self):
        return f'{self.id}-{self.user.username}-{self.perm}'


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
