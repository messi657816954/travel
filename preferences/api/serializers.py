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

        language_id = validated_data.pop('language', None)
        if language_id:
            language = Language.objects.get(id=language_id)
            instance.language = language

        return super().update(instance, validated_data)
