from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, ConfirmString


# UserAdmin继承自ModelAdmin
class UserProfileAdmin(UserAdmin):
    fieldsets = (None, {
        'fields': (
            'username', 'password', 'email', 'roles', 'sex', 'is_superuser', 'is_staff',
            'is_active')}),
    readonly_fields = ('password',)
    list_per_page = 10


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ConfirmString)
