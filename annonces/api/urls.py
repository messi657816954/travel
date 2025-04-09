from django.urls import path

from .views import (
    CreateAnnonceAPIView,
    ConfirmerLivraisonAPIView, PublierAnnonceAPIView, AnnonceDetailAPIView, AnnoncesListAPIView, UpdateAnnonceAPIView,
    AllAnnoncesListAPIView, AnnonceSearchAPIView, DonnerAvisAPIView, UtilisateurAvisView, CancelAnnonceAPIView
)



urlpatterns = [
    path('create/', CreateAnnonceAPIView.as_view(), name='create-annonce'),
    path('update/', UpdateAnnonceAPIView.as_view(), name='update-annonce'),
    path('cancel/', CancelAnnonceAPIView.as_view(), name='cancel-annonce'),
    path('publier/', PublierAnnonceAPIView.as_view(), name='publier-annonce'),
    path('confirmer-livraison/', ConfirmerLivraisonAPIView.as_view(), name='confirmer-livraison'),
    path('detail/', AnnonceDetailAPIView.as_view(), name='detail'),
    path('list/', AnnoncesListAPIView.as_view(), name='list'),
    path('list/all/', AllAnnoncesListAPIView.as_view(), name='list-all'),


    path('search/', AnnonceSearchAPIView.as_view(), name='search'),

    # POST endpoint to create a new avis
    path('avis/donner/', DonnerAvisAPIView.as_view(), name='donner_avis'),

    # GET endpoint to see avis for a specific user
    path('avis/utilisateur/', UtilisateurAvisView.as_view(), name='voir_avis_utilisateur')
]
