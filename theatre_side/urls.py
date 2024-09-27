from django.urls import path

from .views import (
    TheatreEmailVerification,
    TheatreLoginView,
    # TheatreLogoutView,
    TheatreRegisterView,
    TheatreMovieSelectView,
    TheatreShowAddView,
    AvailableShows,
    ShowDeleteView,
    ShowDetailView,
    TheatreDashboardView,
    TheatreProfileView,
    TheaterShowUpdateView
)

urlpatterns = [
    path("register/", TheatreRegisterView.as_view(), name="theatre-register"),
    path(
        "verify-email/", TheatreEmailVerification.as_view(), name="email-verification"
    ),
    path("theatre-login/", TheatreLoginView.as_view(), name="theatre-login"),
    path(
        "theatre-dashboard/", TheatreDashboardView.as_view(), name="theatre-dashboard"
    ),
    path("theatre-profile/", TheatreProfileView.as_view(), name="theatre-profile"),
    path("shows/", TheatreShowAddView.as_view(), name="show-list-create"),
    path("show/<int:pk>/update/", TheaterShowUpdateView.as_view(), name="show-update"),
    path("view-movies/", TheatreMovieSelectView.as_view(), name="view-movies"),
    path(
        "movies/<int:movie_id>/available-shows/",
        AvailableShows.as_view(),
        name="available-shows",
    ),
    path("shows/<int:pk>/", ShowDeleteView.as_view(), name="delete-show"),
    path("show/details/<int:show_id>/", ShowDetailView.as_view(), name="show-details"),
]
