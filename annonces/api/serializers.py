from rest_framework import serializers

from annonces.models import Voyage, Annonce, AvisUser
from commons.models import TypeBagage
from users.api.serializers import UserDetailSerializer
from commons.api.serializers import VilleSerializer
from users.models import User


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
    user_details = UserDetailSerializer(source='user_id', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'date_publication',
            'nombre_kg_dispo', 'montant_par_kg', 'cout_total',
            'active', 'reference', 'voyage', 'user_id','nombre_kg'
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


    def create(self, validated_data):
        validated_data['utilisateur_auteur'] = self.context['request'].user
        return super().create(validated_data)







from django.db.models import Avg, Count

class UserSimpleSerializer(serializers.ModelSerializer):
    # img = serializers.SerializerMethodField()
    # name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user_name']

    # def get_img(self, obj):
    #     # Remplacer par la logique réelle pour récupérer l'image de profil
    #     # Si vous avez un modèle de profil utilisateur avec un champ image, utilisez-le ici
    #     return "-----"
    #
    # def get_name(self, obj):
    #     return obj.get_full_name() or obj.username

class AvisRecusSerializer(serializers.ModelSerializer):
    user_author = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = AvisUser
        fields = ['user_author', 'note', 'date', 'description']

    def get_user_author(self, obj):
        return UserSimpleSerializer(obj.utilisateur_auteur).data

    def get_date(self, obj):
        return obj.date_creation.strftime('%b %Y')

    def get_description(self, obj):
        return obj.commentaire or "**********"

class AvisDonnesSerializer(serializers.ModelSerializer):
    user_note = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = AvisUser
        fields = ['user_note', 'note', 'date', 'description']

    def get_user_note(self, obj):
        return UserSimpleSerializer(obj.utilisateur_note).data

    def get_date(self, obj):
        return obj.date_creation.strftime('%b %Y')

    def get_description(self, obj):
        return obj.commentaire or "**********"





















