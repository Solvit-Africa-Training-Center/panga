from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import VerificationCode, User
from utils.send_email import send_email_custom
from utils.code_generator import random_with_N_digits
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password')

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_active')

    # def clean_password(self):
    #     # Regardless of what the user provides, return the initial value.
    #     # This is done here, rather than on the field, because the
    #     # field does not have access to the initial value
    #     return self.initial["password"]


class SignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    country_code = forms.CharField(max_length=5)
    phone = forms.CharField(max_length=20)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

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
        phone = self.cleaned_data.get("phone")
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("re_password")
        country_code = cleaned_data.get("country_code")
        phonee = cleaned_data.get("phone")

        if country_code and phonee:
            phone_number = country_code + phonee
            if len(phone_number) >= 16:
                raise ValidationError("Phone number is too long.")
            if User.objects.filter(phone=phone_number).exists():
                raise ValidationError("Phone already exists")
            cleaned_data["phone"] = phone_number
        elif not country_code:
            raise ValidationError("Country code is required.")
        elif not phonee:
            raise ValidationError("Phone number is required.")

        # print("Password:", password)
        # print("Re-password:", re_password)
        if password != re_password:
            raise ValidationError("Passwords do not match")
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Phone already exists")

        validate_password(password)
        return cleaned_data

    def save(self, commit=True):

        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            is_active=False,
            phone=self.cleaned_data["phone"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            role=self.cleaned_data["role"]
        )

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
    username = forms.CharField(max_length=50)

    def clean(self):
        identify = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        try:
            user = User.objects.get(username=identify)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone=identify)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=identify)
                except User.DoesNotExist:
                    raise ValidationError("Invalid email phone or password")

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


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full rounded-lg bg-slate-50 dark:bg-[#122017] border border-slate-200 dark:border-[#29382f] px-4 py-2.5 text-slate-900 dark:text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-400"
            })
