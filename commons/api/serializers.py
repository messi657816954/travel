from rest_framework import serializers

from commons.models import Currency, Pays, Ville, TypeBagage


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'symbole']

class PaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ['id', 'intitule', 'code_reference', 'currency']

class VilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ville
        fields = ['id', 'intitule', 'code_reference', 'pays']

class TypeBagageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeBagage
        fields = ['id', 'intitule', 'description']
