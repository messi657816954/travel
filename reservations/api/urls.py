from django.urls import path
from .views import (

    UpdateReserverKilogrammesAPIView, ReservationsListAPIView, ReservationDetailAPIView,
    ConfirmReservationByAnnonceurAPIView, ReserverKilogrammesAPIView, ValidateReservationAPIView,
    CancelReservationByAnnonceurAPIView, CancelReservationByReserveurAPIView, ReceptionColisReservationAPIView,
    LivraisonColisReservationAPIView,

)


urlpatterns = [
    path('reserver/create/', ReserverKilogrammesAPIView.as_view(), name='create-reserver-kilogrammes'),
    path('reserver/update/', UpdateReserverKilogrammesAPIView.as_view(), name='update-reserver-kilogrammes'),
    path('<int:reservation_id>/reserver/validate/', ValidateReservationAPIView.as_view(), name='validate-reserver-kilogrammes'),
    path('<int:reservation_id>/reserver/confirm/annonceur', ConfirmReservationByAnnonceurAPIView.as_view(), name='confirm-reserver-kilogrammes-annonceur'),
    path('<int:reservation_id>/reserver/cancel/annonceur', CancelReservationByAnnonceurAPIView.as_view(), name='cancel-reserver-kilogrammes-annonceur'),
    path('<int:reservation_id>/reserver/cancel/reserveur', CancelReservationByReserveurAPIView.as_view(), name='cancel-reserver-kilogrammes-reserveur'),

    path('reserver/reception/', ReceptionColisReservationAPIView.as_view(), name='reception-reserver-kilogrammes'),
    path('reserver/livraison/', LivraisonColisReservationAPIView.as_view(), name='livraison-reserver-kilogrammes'),

    path('<int:pk>/detail/', ReservationDetailAPIView.as_view(), name='detail'),
    path('list/', ReservationsListAPIView.as_view(), name='list'),

]
