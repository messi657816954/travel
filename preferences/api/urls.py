from django.urls import path
from preferences.api.views import UserPreferenceView, LanguageListView

urlpatterns = [
    path('preferences/', UserPreferenceView.as_view(), name='user-preferences'),
    path('languages/', LanguageListView.as_view(), name='language-list'),
]
