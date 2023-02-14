from django.contrib import admin

from django_flex_reviews.admin import ReviewAdmin
from django_flex_reviews.models import Review

admin.site.register(Review, ReviewAdmin)
