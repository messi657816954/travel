from django.urls import path
from .views import (
    CreateAnnonceAPIView,
    ReserverKilogrammesAPIView,
    ConfirmerReceptionColisAPIView,
    ConfirmerLivraisonAPIView, PublierAnnonceAPIView, AnnonceDetailAPIView, AnnoncesListAPIView
)

urlpatterns = [
    path('create/', CreateAnnonceAPIView.as_view(), name='create-annonce'),
    path('reserver/', ReserverKilogrammesAPIView.as_view(), name='reserver-kilogrammes'),
    path('<int:annonce_id>/publier/', PublierAnnonceAPIView.as_view(), name='publier-annonce'),
    path('<int:reservation_id>/confirmer-reception/', ConfirmerReceptionColisAPIView.as_view(), name='confirmer-reception'),
    path('confirmer-livraison/', ConfirmerLivraisonAPIView.as_view(), name='confirmer-livraison'),
    path('<int:pk>/detail/', AnnonceDetailAPIView.as_view(), name='detail'),
    path('list/', AnnoncesListAPIView.as_view(), name='list'),
]
