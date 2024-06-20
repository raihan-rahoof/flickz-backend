from django.urls import path
from .views import (
    ScreenListCreateView,
    ScreenRetrieveUpdateView,
    ScreenLayoutUpdateView,
    ShowSeatReservationList,
)

urlpatterns = [
    path("add-screen/", ScreenListCreateView.as_view(), name="add-screen"),
    path(
        "update-screen/<int:pk>/",
        ScreenRetrieveUpdateView.as_view(),
        name="screen-detail",
    ),
    path(
        "update-layout/<int:pk>/",
        ScreenLayoutUpdateView.as_view(),
        name="update-layout",
    ),
    path(
        "shows/<int:show_id>/reservations/",
        ShowSeatReservationList.as_view(),
        name="show_seat_reservation_list",
    ),
]
