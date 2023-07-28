from django.contrib import admin

from supergood_reads.admin import ReviewAdmin
from supergood_reads.models import Review

admin.site.register(Review, ReviewAdmin)
