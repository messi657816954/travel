from django.urls import path
from .views import (
    InitiatePaymentView
)


urlpatterns = [
    path('init/', InitiatePaymentView.as_view(), name='init-payment'),
]