from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path(
        "", TemplateView.as_view(template_name="supergood_reads/home.html"), name="home"
    ),
    path(
        "login/",
        views.LoginView.as_view(),
        name="login",
    ),
    path(
        "401/",
        views.Handle401View.as_view(),
        name="401",
    ),
    path(
        "403/",
        views.Handle403View.as_view(),
        name="403",
    ),
    path("reviews/new/", views.CreateReviewView.as_view(), name="create_review"),
    path(
        "reviews/<uuid:pk>/update",
        views.UpdateReviewView.as_view(),
        name="update_review",
    ),
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
        "media/",
        views.MyMediaView.as_view(),
        name="media",
    ),
    path(
        "reviews/",
        views.MyReviewsView.as_view(),
        name="reviews",
    ),
    path(
        "media/book/<uuid:pk>/update",
        views.UpdateMyMediaBookView.as_view(),
        name="update_book",
    ),
    path(
        "media/film/<uuid:pk>/update",
        views.UpdateMyMediaFilmView.as_view(),
        name="update_film",
    ),
    path(
        "media/book/<uuid:pk>/delete/",
        views.DeleteMyMediaBookView.as_view(),
        name="delete_book",
    ),
    path(
        "media/film/<uuid:pk>/delete/",
        views.DeleteMyMediaFilmView.as_view(),
        name="delete_film",
    ),
    path(
        "reviews/<uuid:pk>/delete/",
        views.DeleteReview.as_view(),
        name="delete_review",
    ),
]
