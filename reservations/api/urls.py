from django.urls import path
from .views import (

    UpdateReserverKilogrammesAPIView, ReservationsListAPIView, ReservationDetailAPIView,
    ConfirmReservationByAnnonceurAPIView, ReserverKilogrammesAPIView, PublishReservationAPIView,
    CancelReservationByAnnonceurAPIView, CancelReservationByReserveurAPIView, ReceptionColisReservationAPIView,
    LivraisonColisReservationAPIView, ReservationsListByAnnonceAPIView,

)


urlpatterns = [
    path('reserver/create/', ReserverKilogrammesAPIView.as_view(), name='create-reserver-kilogrammes'),
    path('reserver/update/', UpdateReserverKilogrammesAPIView.as_view(), name='update-reserver-kilogrammes'),
    path('reserver/publish/', PublishReservationAPIView.as_view(), name='validate-reserver-kilogrammes'),
    path('reserver/confirm/annonceur', ConfirmReservationByAnnonceurAPIView.as_view(), name='confirm-reserver-kilogrammes-annonceur'),
    path('reserver/cancel/annonceur', CancelReservationByAnnonceurAPIView.as_view(), name='cancel-reserver-kilogrammes-annonceur'),
    path('reserver/cancel/reserveur', CancelReservationByReserveurAPIView.as_view(), name='cancel-reserver-kilogrammes-reserveur'),

    path('reserver/reception/', ReceptionColisReservationAPIView.as_view(), name='reception-reserver-kilogrammes'),
    path('reserver/livraison/', LivraisonColisReservationAPIView.as_view(), name='livraison-reserver-kilogrammes'),

    path('detail/', ReservationDetailAPIView.as_view(), name='detail'),
    path('list/', ReservationsListAPIView.as_view(), name='list'),
    path('by/annonce/', ReservationsListByAnnonceAPIView.as_view(), name='list-reservation-by-annonce'),

]
