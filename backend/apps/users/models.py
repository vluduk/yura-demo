from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser):
    class Role(models.TextChoices):
        WHOLESALE = 'WHOLESALE', _('Wholesale')
        SERVICE_STATION = 'SERVICE_STATION', _('Service Station')
        RETAIL = 'RETAIL', _('Retail')
        ADMIN = 'ADMIN', _('Admin')

    username = None
    phone = models.CharField(_('phone number'), max_length=20, unique=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RETAIL,
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def __str__(self):
        return self.phone
