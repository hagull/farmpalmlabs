from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, is_password_usable
from django.db.models.signals import pre_save
# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        try:
            user = self.model(
                username=username,
                email=email,
            )

            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            user.set_password(password)
            user.is_active = True
            user.save()
            return user
        except Exception as e:
            print(e)
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        try:
            superuser = self.create_user(
                username=username,
                password=password,
                email=email,
                )
            superuser.is_admin = True
            superuser.is_superuser = True
            superuser.is_active = True
            superuser.is_staff = True
            superuser.save()
            return superuser
        except Exception as e:
            print(e)

class User(AbstractBaseUser):
    user_type = models.CharField(max_length=20)
    objects = UserManager()
    email = models.EmailField(max_length=100, null=False)
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    username = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=12)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True

@receiver(pre_save, sender=User)
def password_hashing(instance, **kwargs):
    if not is_password_usable(instance.password):
        instance.password = make_password(instance.password)
# User모델을 저장하기전에 비밀번호를 hashing과정을 거친후 저장함

# 유저의 프로파일 (즉 유저의 개인정보 및 통합제어기 등의 정보가 들어갈예정)
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    ip_port = models.IntegerField()
    def __str__(self):
        return 'Profile Of User : {}'.format(self.user.username)
# Create your models here.
