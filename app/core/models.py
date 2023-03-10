from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, commit=True, **extra_fields):
        user = self.model(email=self.normalize_email(email), **extra_fields)
        if not email:
            raise ValueError('Users must have an email address.')

        if password:
            user.set_password(password)

        if commit:
            user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password, commit=False)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
