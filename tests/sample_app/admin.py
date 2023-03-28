from django.contrib import admin

from supergood_review_site.admin import ReviewAdmin
from supergood_review_site.models import Review

admin.site.register(Review, ReviewAdmin)
