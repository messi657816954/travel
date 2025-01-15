from django.urls import path
from .views import RegistrationAPIView, VerifyOTPAPIView, LogoutBlacklistTokenUpdateView, MyTokenObtainPairView, \
    UserDetailClientView, InitRegistrationAPIView, PerformRegistrationAPIView, InitForgotPasswordAPIView, \
    ChangePasswordView, PerformForgotPasswordAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('verify/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutBlacklistTokenUpdateView.as_view(), name='logout'),
    path('register/', RegistrationAPIView.as_view(), name='registration'),

    path('user/detail', UserDetailClientView.as_view(), name='User-Detail'),
    path('register/init', InitRegistrationAPIView.as_view(), name='Init-Registration'),
    path('register/perform', RegistrationAPIView.as_view(), name='Perform-Registration'),
    path('forgot/password/init', InitForgotPasswordAPIView.as_view(), name='Init-Forgot-Password'),
    path('forgot/password/perform', PerformForgotPasswordAPIView.as_view(), name='Perform-Forgot-Password'),
    path('password/change', ChangePasswordView.as_view(), name='User-Reset-Password'),

    path('moyens-paiement/', MoyenPaiementListCreateAPIView.as_view(), name='moyen-paiement-list-create'),
    path('moyens-paiement/<int:pk>/', MoyenPaiementDetailAPIView.as_view(), name='moyen-paiement-detail'),


]
