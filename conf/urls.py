
from django.contrib import admin
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ws/api/v1/accounts/', include('users.api.urls')),
    path('ws/api/v1/annonce/', include('annonces.api.urls')),
    path('ws/api/v1/reservation/', include('reservations.api.urls')),
    path('ws/api/v1/referentiel/', include('commons.api.urls')),
    path('ws/api/v1/preference/', include('preferences.api.urls')),
    
]
