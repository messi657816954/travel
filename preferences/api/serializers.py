from rest_framework import serializers
from preferences.models import UserPreference, Language

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code', 'name']

class UserPreferenceSerializer(serializers.ModelSerializer):
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = UserPreference
        fields = ['language', 'theme', 'communication']

    def update(self, instance, validated_data):

        language = validated_data.pop('language', None)
        if language:
            instance.language = language

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """ Personnalise la sortie pour inclure les détails de la langue """
        representation = super().to_representation(instance)
        if instance.language:
            representation['language'] = {
                'id': instance.language.id,
                'code': instance.language.code,
                'name': instance.language.name
            }
        return representation
