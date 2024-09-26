from django.contrib import admin
from django.urls import path
from .views import (
    AdminTokenObtainPairView,
    UserListView,
    BlockUnblockUser,
    MovieListCreateAPIView,
    MovieupdateView,
    TheatreListView,
    TheatreDetailView,
    ApproveTheatreView,
    TheatreRequestsView,
    AdminDashboardView,
    DisapproveTheatreView
)

urlpatterns = [
    path(
        "admin/token",
        AdminTokenObtainPairView.as_view(),
        name="admin_token_obtain_pair",
    ),
    path("admin/user-list", UserListView.as_view(), name="userList"),
    path(
        "admin/user-block-unblock/<int:id>/",
        BlockUnblockUser.as_view(),
        name="user-block-unblock",
    ),
    path("admin/admin-dashboard", AdminDashboardView.as_view(), name="admin-dashboard"),
    path(
        "admin/add-movies/", MovieListCreateAPIView.as_view(), name="movie-list-create"
    ),
    path(
        "admin/update-movie/<int:pk>/", MovieupdateView.as_view(), name="movie-update"
    ),
    path("admin/theatres-list", TheatreListView.as_view(), name="theatre-list"),
    path(
        "admin/theatres-request-list",
        TheatreRequestsView.as_view(),
        name="theatre-request-list",
    ),
    path(
        "admin/view-theatre/<int:pk>/",
        TheatreDetailView.as_view(),
        name="theatre-detail-view",
    ),
    path(
        "admin/theatre-approve/<int:theatre_id>/",
        ApproveTheatreView.as_view(),
        name="approve_theatre",
    ),
    path(
        "admin/theatre-disapprove/<int:theatre_id>/",
        DisapproveTheatreView.as_view(),
        name="disapprove_theatre",
    ),
]
