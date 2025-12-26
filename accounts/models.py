from django.utils import timezone
from django.conf import settings
import random
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxLengthValidator, MinLengthValidator
import datetime

# Create your models here.


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
            user_type=User.ADMIN,
            password=password,
            **extra_fields,
        )

        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    RECORDER = "RECORDER"
    SUPERVISOR = "SUPERVISION"
    FINANCE = "FINANCE"
    ADMIN = "ADMIN"

    ROLE_CHOICES = [
        (RECORDER, 'Recorder'),
        (SUPERVISOR, 'Supervisor'),
        (FINANCE, 'Finance'),
        (ADMIN, 'Admin'),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user_type = models.CharField(
        max_length=25, choices=ROLE_CHOICES, default=RECORDER)

    email = models.EmailField(
        "email address", max_length=255, unique=True, blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    username = models.CharField(_("username"), max_length=100, unique=True)
    # unique phone number as it is a medium for user recognition
    phone_number = models.CharField(
        _("phone number"), max_length=255, unique=True, validators=[
            MinLengthValidator(limit_value=13),
            MaxLengthValidator(limit_value=13)
        ]
    )
    is_active = models.BooleanField(_("is active"), default=True)
    # a admin user; non super-user
    is_staff = models.BooleanField(_("staff"), default=False)
    is_first_login = models.BooleanField(_("staff"), default=True)
    is_admin = models.BooleanField(_("admin"), default=False)  # a admin
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    objects = UserManager()
    USERNAME_FIELD = _("username",)
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def get_full_name(self):
        # The user is identified by their address
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def __str__(self):  # __unicode__ on Python 2O
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class VerificationCode(models.Model):
    SIGNUP = 'SIGNUP'
    RESET_PASSWORD = 'RESET_PASSWORD'
    CHANGE_EMAIL = 'CHANGE_EMAIL'
    VERIFICATION_CODE_CHOICES = (
        (SIGNUP, 'Signup'),
        (RESET_PASSWORD, 'Reset password'),
        (CHANGE_EMAIL, 'Change email'),
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(
        max_length=6, blank=True, null=True)
    is_pending = models.BooleanField(default=True)
    label = models.CharField(
        max_length=255, choices=VERIFICATION_CODE_CHOICES, default=SIGNUP)
    email = models.EmailField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('code', 'user')

    @property
    def valid(self):
        future_time = self.created_on + settings.VERIFICATION_CODE_LIFETIME
        return datetime.now(timezone.utc) < future_time


# ===================================================


class Profile(models.Model):
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"
    SERVICE_PROVIDER = "SERVICE_PROVIDER"

    ROLE_CHOICES = [
        (LANDLORD, 'Landlord'),
        (TENANT, 'Tenant'),
        (SERVICE_PROVIDER, 'Service Provider'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    full_name = models.CharField(max_length=150)

    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"{self.user.email} - {self.role}"


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
        User,
        on_delete=models.CASCADE,
        related_name='verification_codes'
    )
    code = models.CharField(max_length=6)
    label = models.CharField(max_length=30, choices=LABEL_CHOICES)
    email = models.EmailField(blank=True, null=True)
    is_pending = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'code', 'label']),
        ]

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
