from django.urls import path

from . import views

urlpatterns = [
    path("review/", views.CreateReviewView.as_view(), name="create_review"),
    path(
        "film-autocomplete/",
        views.FilmAutocompleteView.as_view(),
        name="film_autocomplete",
    ),
    path(
        "book-autocomplete/",
        views.BookAutocompleteView.as_view(),
        name="book_autocomplete",
    ),
    path(
        "my-media/",
        views.MyMediaView.as_view(),
        name="my_media",
    ),
]
