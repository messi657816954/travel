from rest_framework import generics, permissions
from rest_framework.response import Response
from preferences.models import UserPreference, Language
from preferences.api.serializers import UserPreferenceSerializer, LanguageSerializer

class UserPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, created = UserPreference.objects.get_or_create(user_id=self.request.user)
        return obj

class LanguageListView(generics.ListAPIView):
    queryset = Language.objects.filter(active=True)
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]
