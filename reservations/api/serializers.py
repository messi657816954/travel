from rest_framework import serializers

from annonces.models import Reservation
from annonces.api.serializers import AnnonceSerializer
from users.api.serializers import UserDetailSerializer


class ReservationSerializer(serializers.ModelSerializer):
    annonce_details = AnnonceSerializer(source="annonce", read_only=True)
    user_details = UserDetailSerializer(source='user', read_only=True)
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('date_publication', 'published', 'active','code_reception','code_livraison')
