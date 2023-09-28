# users/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, role, otp=None, **kwargs):
        if not mobile:
            raise ValueError('Mobile number is required.')
        if not role:
            raise ValueError('User role is required.')

        user = self.model(
            mobile=mobile,
            role=role,
            **kwargs
        )

        if(otp):
            user.otp = otp 

        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, role, password, otp=None, **kwargs):
        user = self.create_user(
            mobile=mobile,
            role=role,
            otp=otp,
            **kwargs
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6, null=True)
    role = models.CharField(max_length=10)  # 'advisor' or 'user'
    is_active = models.BooleanField(default=True)
    is_advisor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['role', 'otp']

    def verify_otp(self, otp):
        # Dummy logic for OTP verification
        return self.otp == otp

    def __str__(self):
        return self.mobile



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)