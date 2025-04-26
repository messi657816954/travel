
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ws/api/v1/accounts/', include('users.api.urls')),
    path('ws/api/v1/annonce/', include('annonces.api.urls')),
    path('ws/api/v1/reservation/', include('reservations.api.urls')),
    path('ws/api/v1/referentiel/', include('commons.api.urls')),
    path('ws/api/v1/preference/', include('preferences.api.urls')),
    path('ws/api/v1/', include('bank_details.api.urls')),
    path('ws/api/v1/account/', include('transactions.api.urls')),
    path('ws/api/v1/payment/', include('payments.api.urls')),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
