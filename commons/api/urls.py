from django.urls import path
from .views import (
    CurrencyListCreateAPIView, CurrencyDetailAPIView,
    PaysListCreateAPIView, PaysDetailAPIView,
    VilleListCreateAPIView, VilleDetailAPIView,
    TypeBagageListCreateAPIView, TypeBagageDetailAPIView, VilleAutocompleteAPIView
)

urlpatterns = [
    # URLs pour Currency
    path('currencies/', CurrencyListCreateAPIView.as_view(), name='currency-list-create'),
    path('currencies/<int:pk>/', CurrencyDetailAPIView.as_view(), name='currency-detail'),

    # URLs pour Pays
    path('pays/', PaysListCreateAPIView.as_view(), name='pays-list-create'),
    path('pays/<int:pk>/', PaysDetailAPIView.as_view(), name='pays-detail'),

    # URLs pour Ville
    path('villes/', VilleListCreateAPIView.as_view(), name='ville-list-create'),
    path('villes/<int:pk>/', VilleDetailAPIView.as_view(), name='ville-detail'),

    # URLs pour TypeBagage
    path('type-bagages/', TypeBagageListCreateAPIView.as_view(), name='type-bagage-list-create'),
    path('type-bagages/<int:pk>/', TypeBagageDetailAPIView.as_view(), name='type-bagage-detail'),


    path('ville/autocomplete', VilleAutocompleteAPIView.as_view(), name='ville-auto-complete'),
]
