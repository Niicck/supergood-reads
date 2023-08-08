from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("app/", include("supergood_reads.urls")),
]
