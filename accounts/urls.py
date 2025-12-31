from django.urls import path
from .views import signup_view, verify_account_view, login_view, logout_view, forgot_password_view, reset_password_view, change_password_view

# app_name = 'accounts'


urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("verify/", verify_account_view, name="verify_account"),
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("reset-password/", reset_password_view, name="reset_password"),
    path("change-password/", change_password_view, name="change_password"),
]
