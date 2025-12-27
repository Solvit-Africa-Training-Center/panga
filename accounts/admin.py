from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .models import Profile, VerificationCode


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    # fk_name = 'user'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')


try:
    admin.site.unregister(User)
except Exception:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(VerificationCode)
