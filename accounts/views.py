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
                request, "Account created. Check your email for the activation code.")
            return redirect("verify_account")
        else:
            print(form.errors)

    return render(request, "accounts/c_register.html", {"form": form})


def verify_account_view(request):
    form = VerificationCodeForm()

    if request.method == "POST":
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            messages.success(request, "Account activated. You can now login.")
            return redirect("login")
        else:
            return redirect("verify_account")

    return render(request, "accounts/c_email_verify.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = CustomLoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            # messages.success(request, "Welcome to Gukodesha!")
            if request.user.role == "LANDLORD":
                return redirect('landlord_dashboard')
            return redirect("home")

    return render(request, "accounts/c_login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)

    if form.is_valid():
        code = form.send_reset_code()
        request.session["reset_email"] = form.cleaned_data["email"]
        messages.success(request, "Check your email for the reset code.")
        return redirect("reset_password")

    return render(request, "accounts/c_forgot_password.html", {"form": form})


def reset_password_view(request):
    email = request.session.get("reset_email")
    if not email:
        messages.error(
            request, "No email found. Start the reset process again.")
        return redirect("forgot_password")

    form = ResetPasswordForm(request.POST or None, email=email)

    if form.is_valid():
        form.save()
        request.session.pop("reset_email", None)
        messages.success(request, "Password reset successfully.")
        return redirect("login")

    return render(request, "accounts/c_reset_password.html", {"form": form})


@login_required
def change_password_view(request):
    form = ChangePasswordForm(user=request.user, data=request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Password changed successfully.")
        return redirect("login")

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
