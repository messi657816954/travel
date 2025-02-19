from rest_framework import serializers

from annonces.models import Reservation
from annonces.api.serializers import AnnonceDetailSerializer


class ReservationSerializer(serializers.ModelSerializer):
    annonce_details = AnnonceDetailSerializer(source="annonce", read_only=True)
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('date_publication', 'published', 'active','code_reception','code_livraison')
