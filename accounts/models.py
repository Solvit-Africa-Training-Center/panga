import random
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _


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
