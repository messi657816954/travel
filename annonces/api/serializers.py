from rest_framework import serializers

from annonces.models import Voyage, Annonce, AvisUser
from commons.models import TypeBagage
from users.api.serializers import UserDetailSerializer
from commons.api.serializers import VilleSerializer


class TypeBagageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeBagage
        fields = '__all__'


class VoyageSerializer(serializers.ModelSerializer):
    departure_details = VilleSerializer(source='provenance', read_only=True)
    destination_details = VilleSerializer(source='destination', read_only=True)
    class Meta:
        model = Voyage
        fields = [
            'id', 'date_depart', 'provenance', 'departure_details', 'destination', 'destination_details',
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
        #read_only_fields = ('date_publication', 'commission','published',
         #                 'revenue_transporteur', 'reference')


class AnnonceDetailSerializer(serializers.ModelSerializer):
    voyage_details = VoyageSerializer(source='voyage', read_only=True)
    user_details = UserDetailSerializer(source='user_id', read_only=True)

    class Meta:
        model = Annonce
        fields = '__all__'



class AvisUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvisUser
        fields = '__all__'
        read_only_fields = ['utilisateur_auteur']

    def validate(self, data):
        """
        Validate that either reservation or annonce is provided, but not both.
        Also check for duplicates.
        """
        reservation = data.get('reservation')
        annonce = data.get('annonce')

        if reservation and annonce:
            raise serializers.ValidationError("Un avis ne peut pas être lié à la fois à une réservation et à une annonce.")

        if not reservation and not annonce:
            raise serializers.ValidationError("Un avis doit être lié soit à une réservation, soit à une annonce.")

        # Check for duplicates
        utilisateur_auteur = self.context['request'].user
        utilisateur_note = data.get('utilisateur_note')

        if reservation:
            if AvisUser.objects.filter(
                utilisateur_auteur=utilisateur_auteur,
                utilisateur_note=utilisateur_note,
                reservation=reservation
            ).exists():
                raise serializers.ValidationError("Vous avez déjà donné un avis pour cette réservation.")

        if annonce:
            if AvisUser.objects.filter(
                utilisateur_auteur=utilisateur_auteur,
                utilisateur_note=utilisateur_note,
                annonce=annonce
            ).exists():
                raise serializers.ValidationError("Vous avez déjà donné un avis pour cette annonce.")

        return data
