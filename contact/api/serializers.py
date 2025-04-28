from rest_framework import serializers

from contact.models import ContactUser


class ContactUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUser
        fields = '__all__'