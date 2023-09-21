from django.contrib import admin

from supergood_reads.admin import UserSettingsAdmin
from supergood_reads.models import UserSettings

admin.site.register(UserSettings, UserSettingsAdmin)
