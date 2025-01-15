from django.urls import path
from .views import (

    ReserverKilogrammesAPIView,

)


urlpatterns = [
    path('annonces/<int:annonce_id>/reserver/', ReserverKilogrammesAPIView.as_view(), name='reserver-kilogrammes'),
]
