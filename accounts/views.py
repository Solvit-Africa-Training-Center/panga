from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User

from .forms import *
from .models import VerificationCode
from utils.send_email import send_email_custom
from utils.code_generator import random_with_N_digits


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignupForm()

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account created. Check your email for the activation code."
            )
            return redirect("verify_account")
        else:
            print(form.errors)

    return render(request, "accounts/c_register.html", {"form": form})


def verify_account_view(request):
    form = VerificationCodeForm()

    if request.method == "POST":
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                code_obj = VerificationCode.objects.get(
                    code=code,
                    label=VerificationCode.SIGNUP,
                    is_pending=True
                )
            except VerificationCode.DoesNotExist:
                messages.error(request, "Invalid or expired code")
                return redirect("verify_account")

            if not code_obj.is_valid:
                messages.error(request, "Code expired")
                return redirect("verify_account")

            user = code_obj.user
            user.is_active = True
            user.save()

            code_obj.is_pending = False
            code_obj.save()

            messages.success(request, "Account activated. You can now login.")
            return redirect("login")

    return render(request, "accounts/c_email_verify.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = CustomLoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            # messages.success(request, "Welcome to Gukodesha!")
            return redirect("home")

    return render(request, "accounts/c_login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def forgot_password_view(request):
    form = ForgotPasswordForm()

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)

            code = random_with_N_digits(6)
            VerificationCode.objects.create(
                user=user,
                code=code,
                label=VerificationCode.RESET_PASSWORD,
                email=email
            )

            context = {
                "title": "Reset your password",
                "message": "Use the following code to reset your password:",
                "code": code,
            }
            send_email_custom(
                email,
                "Password reset code",
                "email/code_email.html",
                context
            )

            request.session["reset_email"] = email
            messages.success(request, "Check your email for the reset code.")
            return redirect("reset_password")
        else:
            messages.error(request, "No account with this email")
            print(form.errors)

    return render(request, "accounts/c_forgot_password.html", {"form": form})


def reset_password_view(request):
    form = ResetPasswordForm()
    code_form = VerificationCodeForm()

    if request.method == "POST":
        code_form = VerificationCodeForm(request.POST)
        form = ResetPasswordForm(request.POST)

        if code_form.is_valid() and form.is_valid():
            code = code_form.cleaned_data["code"]
            email = request.session.get("reset_email")

            try:
                code_obj = VerificationCode.objects.get(
                    code=code,
                    label=VerificationCode.RESET_PASSWORD,
                    email=email,
                    is_pending=True
                )
            except VerificationCode.DoesNotExist:
                messages.error(request, "Invalid code")
                return redirect("reset_password")

            if not code_obj.is_valid:
                messages.error(request, "Code expired")
                return redirect("reset_password")

            user = code_obj.user
            user.set_password(form.cleaned_data["new_password"])
            user.save()

            code_obj.is_pending = False
            code_obj.save()

            request.session.pop("reset_email", None)

            messages.success(request, "Password reset successfully.")
            return redirect("login")
        else:
            print(form.errors)

    return render(
        request,
        "accounts/c_reset_password.html",
        {
            "form": form,
            "code_form": code_form
        }
    )


@login_required
def change_password_view(request):
    form = ChangePasswordForm()

    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user

            if not user.check_password(form.cleaned_data["old_password"]):
                messages.error(request, "Old password is incorrect")
                return redirect("change_password")

            user.set_password(form.cleaned_data["new_password"])
            user.save()

            messages.success(request, "Password changed successfully.")
            return redirect("login")
        else:
            print(form.errors)

    return render(request, "accounts/c_reset_password.html", {"form": form})


@login_required
def profile_update_view(request):
    user = request.user

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("update_profile")
        else:
            messages.error(request, "Operation Failed")
    else:
        form = UserProfileForm(instance=user)

    return render(request, "properties/all/edit_profile.html", {
        "form": form
    })
