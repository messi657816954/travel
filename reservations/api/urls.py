from django.urls import path
from .views import (

    CancelReservationAPIView, CreateReserverKilogrammesAPIView,
    UpdateReserverKilogrammesAPIView, ReservationsListAPIView, ReservationDetailAPIView,

)


urlpatterns = [
    path('reserver/create/', CreateReserverKilogrammesAPIView.as_view(), name='create-reserver-kilogrammes'),
    path('annonces/<int:annonce_id>/reserver/update/', UpdateReserverKilogrammesAPIView.as_view(), name='update-reserver-kilogrammes'),
    path('annonces/<int:reservation_id>/reserver/cancel/', CancelReservationAPIView.as_view(), name='cancel-reserver-kilogrammes'),
    path('<int:pk>/detail/', ReservationDetailAPIView.as_view(), name='detail'),
    path('list/', ReservationsListAPIView.as_view(), name='list'),
]
