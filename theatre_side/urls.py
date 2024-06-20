from django.urls import path

from .views import (
    TheatreEmailVerification,
    TheatreLoginView,
    # TheatreLogoutView,
    TheatreRegisterView,
    TheatreMovieSelectView,
    TheatreShowAddView,
    AvailableShows
)

urlpatterns = [
    path("register/", TheatreRegisterView.as_view(), name="theatre-register"),
    path(
        "verify-email/", TheatreEmailVerification.as_view(), name="email-verification"
    ),
    path("theatre-login/", TheatreLoginView.as_view(), name="theatre-login"),
    # path("theatre-logout/", TheatreLogoutView.as_view(), name="theatre-logout"),
    path("shows/", TheatreShowAddView.as_view(), name="show-list-create"),
    path("view-movies/", TheatreMovieSelectView.as_view(), name="view-movies"),
    path(
        "movies/<int:movie_id>/available-shows/",
        AvailableShows.as_view(),
        name="available-shows"
    ),
]
