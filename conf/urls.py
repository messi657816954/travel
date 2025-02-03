
from django.contrib import admin
from django.urls import path,include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ws/api/v1/accounts/', include('users.api.urls')),
    path('ws/api/v1/annonce/', include('annonces.api.urls')),
    path('ws/api/v1/reservation/', include('reservations.api.urls')),
    path('ws/api/v1/referentiel/', include('commons.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    
]
