from django.contrib import admin
from django.urls import include, path

from supergood_reads.urls import handler401, handler403

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("app/", include("supergood_reads.urls")),
]

handler401 = handler401
handler403 = handler403
