from django.contrib import admin
from django.urls import include, path

from supergood_reads.views import Handle403View

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("app/", include("supergood_reads.urls")),
]

handler403 = Handle403View.as_view()
