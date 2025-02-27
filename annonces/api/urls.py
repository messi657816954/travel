from django.urls import path

from .views import (
    CreateAnnonceAPIView,
    ConfirmerLivraisonAPIView, PublierAnnonceAPIView, AnnonceDetailAPIView, AnnoncesListAPIView, UpdateAnnonceAPIView,
    AllAnnoncesListAPIView, AnnonceSearchAPIView, DonnerAvisAPIView, ListerAvisRecusAPIView, VoirAvisUtilisateurAPIView
)



urlpatterns = [
    path('create/', CreateAnnonceAPIView.as_view(), name='create-annonce'),
    path('update/', UpdateAnnonceAPIView.as_view(), name='update-annonce'),
    path('publier/', PublierAnnonceAPIView.as_view(), name='publier-annonce'),
    path('confirmer-livraison/', ConfirmerLivraisonAPIView.as_view(), name='confirmer-livraison'),
    path('detail/', AnnonceDetailAPIView.as_view(), name='detail'),
    path('list/', AnnoncesListAPIView.as_view(), name='list'),
    path('list/all/', AllAnnoncesListAPIView.as_view(), name='list-all'),


    path('search/', AnnonceSearchAPIView.as_view(), name='search'),

    # POST endpoint to create a new avis
    path('donner/', DonnerAvisAPIView.as_view(), name='donner_avis'),

    # GET endpoint to list avis received by the authenticated user
    path('recus/', ListerAvisRecusAPIView.as_view(), name='lister_avis_recus'),

    # GET endpoint to see avis for a specific user
    path('utilisateur/', VoirAvisUtilisateurAPIView.as_view(), name='voir_avis_utilisateur')
]
