from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import Group
from user.models import Activity, UserPerm

admin.site.unregister(Group)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'info', 'create_time')
    list_filter = ('user',)


class UserPermAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'perm')


admin.site.register(Activity, ActivityAdmin)
admin.site.register(UserPerm, UserPermAdmin)
