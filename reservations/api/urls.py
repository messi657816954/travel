from django.urls import path
from .views import (

    CancelReservationAPIView, CreateReserverKilogrammesAPIView,
    UpdateReserverKilogrammesAPIView,

)


urlpatterns = [
    path('annonces/reserver/create/', CreateReserverKilogrammesAPIView.as_view(), name='create-reserver-kilogrammes'),
    path('annonces/reserver/update', UpdateReserverKilogrammesAPIView.as_view(), name='update-reserver-kilogrammes'),
    path('annonces/<int:reservation_id>/reserver/cancel', CancelReservationAPIView.as_view(), name='cancel-reserver-kilogrammes'),
]
