from django.urls import path
from .views import (
    InitiatePaymentView, SetupIntendPaymentView, PaymentWithSavedCardView
)


urlpatterns = [
    path('init/', InitiatePaymentView.as_view(), name='init-payment'),
    path('create/', PaymentWithSavedCardView.as_view(), name='create-payment'),
    path('create-setup-intent/', SetupIntendPaymentView.as_view(), name='setup-payment'),
]