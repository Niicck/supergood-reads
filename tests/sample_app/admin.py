from django.contrib import admin

from supergood_reads.admin import ReviewAdmin, UserSettingsAdmin
from supergood_reads.models import Review, UserSettings

admin.site.register(Review, ReviewAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
