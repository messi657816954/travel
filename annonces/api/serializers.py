from rest_framework import serializers

from annonces.models import Voyage, Annonce


class VoyageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voyage
        fields = [
            'id', 'date_depart', 'provenance', 'destination',
            'agence_voyage', 'code_reservation'
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
            'id', 'date_publication', 'est_publie', 'type_bagage_auto',
            'nombre_kg_dispo', 'montant_par_kg', 'cout_total',
            'statut',
            'est_actif', 'reference', 'voyage', 'voyage_details', 'createur'
        ]
        # read_only_fields = ('date_publication', 'cout_total', 'commission',
        #                   'revenue_transporteur', 'reference')
