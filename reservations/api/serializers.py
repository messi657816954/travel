from rest_framework import serializers

from annonces.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('date_publication', 'published', 'active','code_reception','code_livraison')
