from rest_framework import serializers
from preferences.models import UserPreference, Language

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code', 'name']

class UserPreferenceSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()

    class Meta:
        model = UserPreference
        fields = ['language', 'theme', 'communication']

    def update(self, instance, validated_data):

        language_data = validated_data.pop('language', None)
        if language_data:
            language = Language.objects.get(id=language_data['id'])
            instance.language = language

        return super().update(instance, validated_data)
