from rest_framework import serializers

from annonces.models import Reservation
from annonces.api.serializers import AnnonceDetailSerializer
from users.api.serializers import UserDetailSerializer


class ReservationSerializer(serializers.ModelSerializer):
    annonce_details = AnnonceDetailSerializer(source="annonce", read_only=True)
    user_details = UserDetailSerializer(source='user', read_only=True)
    code_reception = serializers.SerializerMethodField()
    code_livraison = serializers.SerializerMethodField()
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('code_reception','code_livraison')

    def get_code_reception(self, obj):
        return obj.code_reception is not None

    def get_code_livraison(self, obj):
        return obj.code_livraison is not None

class ReservationDetailsSerializer(serializers.ModelSerializer):
    code_reception = serializers.SerializerMethodField()
    code_livraison = serializers.SerializerMethodField()
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('code_reception','code_livraison')

    def get_code_reception(self, obj):
        return obj.code_reception is not None

    def get_code_livraison(self, obj):
        return obj.code_livraison is not None
