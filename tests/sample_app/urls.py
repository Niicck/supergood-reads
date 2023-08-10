from django.contrib import admin
from django.urls import include, path

from supergood_reads.views.views import Handle403View

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("reads-app/", include("supergood_reads.urls")),
    path("reads-app/auth/", include("tests.sample_app.basic_auth.urls")),
]

handler403 = Handle403View.as_view()
