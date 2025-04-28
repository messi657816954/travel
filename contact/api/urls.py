from django.urls import path
from views import CreateContactUserAPIView

urlpatterns = [
    path('send-message/', CreateContactUserAPIView.as_view(), name='send-message'),
]