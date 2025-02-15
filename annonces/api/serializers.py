from rest_framework import serializers

from annonces.models import Voyage, Annonce
from commons.models import TypeBagage


class TypeBagageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeBagage
        fields = '__all__'


class VoyageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voyage
        fields = [
            'id', 'date_depart', 'provenance', 'destination',
            'agence_voyage', 'code_reservation','moyen_transport'
        ]
        extra_kwargs = {
            'code_reservation': {'required': False, 'allow_blank': True},
            'agence_voyage': {'required': False, 'allow_blank': True}
        }


class AnnonceSerializer(serializers.ModelSerializer):
    voyage_details = VoyageSerializer(source='voyage', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'date_publication',
            'nombre_kg_dispo', 'montant_par_kg', 'cout_total',
            'active', 'reference', 'voyage', 'voyage_details', 'user_id'
        ]
        read_only_fields = ('date_publication', 'commission','published',
                          'revenue_transporteur', 'reference')


class AnnonceDetailSerializer(serializers.ModelSerializer):
    voyage_details = VoyageSerializer(source='voyage', read_only=True)

    class Meta:
        model = Annonce
        fields = '__all__'

