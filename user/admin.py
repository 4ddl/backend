from django.contrib import admin

# Register your models here.

from django.contrib.auth.models import Group
from user.models import Activity, User, UserPerm, Perm

admin.site.unregister(Group)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'info', 'create_time')
    list_filter = ('user',)


admin.site.register(Activity, ActivityAdmin)
admin.site.register(UserPerm)
admin.site.register(Perm)
