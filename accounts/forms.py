from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Profile, VerificationCode
from utils.send_email import send_email_custom
from utils.code_generator import random_with_N_digits


class SignupForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)
    country_code = forms.CharField(max_length=5)
    phone = forms.CharField(max_length=20)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    password = forms.CharField(widget=forms.PasswordInput)
    re_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "password", "re_password")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("re_password")
        country_code = cleaned_data.get("country_code")
        phonee = cleaned_data.get("phone")

        if country_code and phonee:
            phone_number = country_code + phonee
            cleaned_data["phone"] = phone_number
        elif not country_code:
            raise ValidationError("Country code is required.")
        elif not phonee:
            raise ValidationError("Phone number is required.")

        print("Password:", password)
        print("Re-password:", re_password)
        if password != re_password:
            raise ValidationError("Passwords do not match")

        validate_password(password)
        return cleaned_data

    def save(self, commit=True):

        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            is_active=False
        )

        profile = user.profile
        profile.full_name = self.cleaned_data["full_name"]
        profile.phone = self.cleaned_data["phone"]
        profile.role = self.cleaned_data["role"]
        profile.save()

        code = random_with_N_digits(6)
        VerificationCode.objects.create(
            user=user,
            code=code,
            label=VerificationCode.SIGNUP,
            email=user.email
        )

        context = {
            "title": "Account Activation",
            "message": "Use the following code to activate your account:",
            "code": code,
            "email": user.email
        }
        send_email_custom(
            user.email,
            "Activate your account",
            "email/code_email.html",
            context)

        return user


class VerificationCodeForm(forms.Form):
    code = forms.CharField(max_length=6)


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Invalid email or password")

        if not user.is_active:
            raise ValidationError("Account is not activated")

        self.cleaned_data["username"] = user.username
        return super().clean()


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account with this email")
        return email


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password")
        password2 = cleaned_data.get("repeat_password")

        if password1 != password2:
            raise ValidationError("Passwords do not match")

        validate_password(password1)
        return cleaned_data


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        repeat_password = cleaned_data.get("repeat_password")

        if new_password != repeat_password:
            raise ValidationError("Passwords do not match")

        validate_password(new_password)
        return cleaned_data
