from django.urls import path
from .views import (
    CreateAnnonceAPIView,
    ReserverKilogrammesAPIView,
    ConfirmerReceptionColisAPIView,
    ConfirmerLivraisonAPIView
)

urlpatterns = [
    path('annonces/create/', CreateAnnonceAPIView.as_view(), name='create-annonce'),
    path('annonces/<int:annonce_id>/reserver/', ReserverKilogrammesAPIView.as_view(), name='reserver-kilogrammes'),
    path('reservations/<int:reservation_id>/confirmer-reception/', ConfirmerReceptionColisAPIView.as_view(), name='confirmer-reception'),
    path('reservations/<int:reservation_id>/confirmer-livraison/', ConfirmerLivraisonAPIView.as_view(), name='confirmer-livraison'),
]
