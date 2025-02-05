from django.urls import path
from .views import (
    CreateAnnonceAPIView,
    ConfirmerLivraisonAPIView, PublierAnnonceAPIView, AnnonceDetailAPIView, AnnoncesListAPIView, UpdateAnnonceAPIView,
    AllAnnoncesListAPIView
)



urlpatterns = [
    path('create/', CreateAnnonceAPIView.as_view(), name='create-annonce'),
    path('update/', UpdateAnnonceAPIView.as_view(), name='update-annonce'),
    path('publier/', PublierAnnonceAPIView.as_view(), name='publier-annonce'),
    path('confirmer-livraison/', ConfirmerLivraisonAPIView.as_view(), name='confirmer-livraison'),
    path('detail/', AnnonceDetailAPIView.as_view(), name='detail'),
    path('list/', AnnoncesListAPIView.as_view(), name='list'),
    path('list/all/', AllAnnoncesListAPIView.as_view(), name='list-all'),
]
