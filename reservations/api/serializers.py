from rest_framework import serializers

from annonces.models import Voyage, Annonce


class VoyageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voyage
        fields = '__all__'

class AnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annonce
        fields = '__all__'
        read_only_fields = ('date_publication', 'est_publie', 'est_actif')
