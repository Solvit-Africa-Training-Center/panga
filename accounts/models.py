# this is the latest version

import random
import uuid
from django.conf import settings
from django.db import models
# from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxLengthValidator, MinLengthValidator


class UserManager(BaseUserManager):

    def create_user(self, username, first_name, last_name, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, username, first_name, last_name, password=None, **extra_fields
    ):
        """
        Creates and saves a admin with the given email and password.
        """
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=User.ADMIN,
            password=password,
            **extra_fields,
        )

        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"
    SERVICE_PROVIDER = "SERVICE_PROVIDER"
    ADMIN = "ADMIN"

    ROLE_CHOICES = [
        (LANDLORD, 'Landlord'),
        (TENANT, 'Tenant'),
        (SERVICE_PROVIDER, 'Service Provider'),
        (ADMIN, 'ADMIN'),
    ]
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    email = models.EmailField(
        "email address", max_length=255, unique=True, blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    username = models.CharField(_("username"), max_length=100, unique=True)

    phone = models.CharField(
        _("phone number"), max_length=255, unique=True, validators=[
            MinLengthValidator(limit_value=13),
            MaxLengthValidator(limit_value=15)
        ]
    )
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(_("created on"), auto_now_add=True)
    objects = UserManager()
    is_staff = models.BooleanField(_("staff"), default=False)
    is_first_login = models.BooleanField(_("staff"), default=True)
    is_admin = models.BooleanField(_("admin"), default=False)
    USERNAME_FIELD = _("username")
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True


class VerificationCode(models.Model):
    SIGNUP = 'SIGNUP'
    RESET_PASSWORD = 'RESET_PASSWORD'
    CHANGE_EMAIL = 'CHANGE_EMAIL'

    LABEL_CHOICES = [
        (SIGNUP, 'Signup'),
        (RESET_PASSWORD, 'Reset password'),
        (CHANGE_EMAIL, 'Change email'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name='verification_codes'
    )
    code = models.CharField(max_length=6)
    label = models.CharField(
        max_length=30, choices=LABEL_CHOICES, default=SIGNUP)
    email = models.EmailField(max_length=255, blank=True, null=True)
    is_pending = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'code', 'label']),
        ]
        unique_together = ('code', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.label} - {self.code}"

    @property
    def is_valid(self):
        expiration_time = self.created_on + settings.VERIFICATION_CODE_LIFETIME
        return timezone.now() < expiration_time and self.is_pending

    @staticmethod
    def generate_code(n=6):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return random.randint(range_start, range_end)
