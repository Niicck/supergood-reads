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
    path(
        "my-media/book/<uuid:pk>/",
        views.UpdateMyMediaBookView.as_view(),
        name="my_media_book_update",
    ),
    path(
        "my-media/film/<uuid:pk>/",
        views.UpdateMyMediaFilmView.as_view(),
        name="my_media_film_update",
    ),
    path(
        "my-media/book/<uuid:pk>/delete/",
        views.DeleteMyMediaBookView.as_view(),
        name="my_media_book_delete",
    ),
    path(
        "my-media/film/<uuid:pk>/delete/",
        views.DeleteMyMediaFilmView.as_view(),
        name="my_media_film_delete",
    ),
]
