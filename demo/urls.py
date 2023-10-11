from django.contrib import admin
from django.urls import include, path

from supergood_reads.views.views import Handle403View

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("/", include("supergood_reads.urls")),
    path("auth/", include("demo.basic_auth.urls")),
]

handler403 = Handle403View.as_view()
