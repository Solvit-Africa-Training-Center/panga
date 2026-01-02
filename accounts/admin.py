from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.forms import UserAdminCreationForm, UserAdminChangeForm
from django.contrib import admin
from accounts.models import VerificationCode, User
# Register your models here.
admin.site.register(VerificationCode)


class UserAdmin(BaseUserAdmin, admin.ModelAdmin,):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_active",
        "phone"

    )
    list_filter = (
        "role",
        "is_active",

    )
    fieldsets = (
        (None, {"fields": (
            "username",
            "email",
            "password",

        )}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "role",

                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    'groups',
                    'user_permissions',

                )
            },
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": (
            "email",
            "first_name",
            "last_name",
            "username",
            "role",
            "phone",
            "password"

        )}),
    )
    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
        "phone",
    )

    ordering = ("first_name", "last_name")
    filter_horizontal = ()
    actions = [
        "disable_users",
        "enable_users",
    ]

    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)

    def disable_users(self, request, queryset):
        queryset.update(is_active=False)

    def enable_users(self, request, queryset):
        queryset.update(is_active=True)

    def has_add_permission(self, request) -> bool:
        if request.user.is_staff:
            return True
        return False


admin.site.register(User, UserAdmin)
