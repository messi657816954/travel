from rest_framework import serializers

from commons.models import Currency, Pays, Ville, TypeBagage


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'symbole']

class PaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ['id', 'country_code', 'iso_code2', 'iso_code3','label','label_en','currency','digit_code']

class VilleSerializer(serializers.ModelSerializer):
    pays_details = VoyageSerializer(source='pays', read_only=True)
    class Meta:
        model = Ville
        fields = ['id', 'intitule', 'code_reference', 'pays']

class TypeBagageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeBagage
        fields = ['id', 'intitule', 'description']
