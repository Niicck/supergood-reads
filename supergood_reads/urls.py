from django.urls import path
from django.views.generic import TemplateView

from supergood_reads.views import views

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="supergood_reads/views/home.html"),
        name="home",
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
        "media-type-autocomplete/",
        views.MediaTypeAutocompleteView.as_view(),
        name="media_type_autocomplete",
    ),
    path(
        "library/",
        views.LibraryView.as_view(),
        name="library",
    ),
    path(
        "media/search/",
        views.MediaTypeSearchView.as_view(),
        name="media_search",
    ),
    path(
        "media-type-choices-api/",
        views.MediaTypeChoicesApiView.as_view(),
        name="media_type_choices_api",
    ),
    path(
        "genres-api/",
        views.GenreApiView.as_view(),
        name="genres_api",
    ),
    path(
        "countries-api/",
        views.CountryApiView.as_view(),
        name="countries_api",
    ),
    path(
        "reviews/",
        views.MyReviewsView.as_view(),
        name="reviews",
    ),
    path("media/new/", views.MediaFormView.as_view(), name="create_media"),
    path(
        "media/book/<uuid:pk>/update",
        views.UpdateBookView.as_view(),
        name="update_book",
    ),
    path(
        "media/film/<uuid:pk>/update",
        views.UpdateFilmView.as_view(),
        name="update_film",
    ),
    path(
        "media/book/<uuid:pk>/delete/",
        views.DeleteBookView.as_view(),
        name="delete_book",
    ),
    path(
        "media/film/<uuid:pk>/delete/",
        views.DeleteFilmView.as_view(),
        name="delete_film",
    ),
    path(
        "reviews/<uuid:pk>/delete/",
        views.DeleteReview.as_view(),
        name="delete_review",
    ),
]
