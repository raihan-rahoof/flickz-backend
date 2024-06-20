from django.contrib import admin
from django.urls import path
from .views import CreateCheckoutSessionView,PaymentSuccessView,PaymentCancelView,TicketsListView


urlpatterns = [
    path("checkout/", CreateCheckoutSessionView.as_view(), name="chekout"),
    path("payment-success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payment-cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
    path("show-tickets/",TicketsListView.as_view(),name='list-tickets')
]
