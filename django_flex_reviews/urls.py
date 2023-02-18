from django.urls import path

from . import views

urlpatterns = [
    path("review/", views.CreateReviewView.as_view(), name="create_review"),
]
