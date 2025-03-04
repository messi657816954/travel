from django.urls import path
from .views import RegistrationAPIView, VerifyOTPAPIView, LogoutBlacklistTokenUpdateView, MyTokenObtainPairView, \
    UserDetailClientView, InitRegistrationAPIView, InitForgotPasswordAPIView, \
    ChangePasswordView, PerformForgotPasswordAPIView, MoyenPaiementListCreateAPIView, MoyenPaiementDetailAPIView, \
    InitierPaiementAPIView, PerformOtpAPIView, InitPhoneOtpAPIView, InitUpdateEmailAPIView, UpdateEmailAPIView, \
    UpdatePhoneAPIView, InitUpdatePhoneAPIView

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

urlpatterns = [

    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('verify/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    # path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutBlacklistTokenUpdateView.as_view(), name='logout'),
    # path('register/', RegistrationAPIView.as_view(), name='registration'),

    path('user/detail', UserDetailClientView.as_view(), name='User-Detail'),
    path('register/init', InitRegistrationAPIView.as_view(), name='Init-Registration'),
    path('register/perform', RegistrationAPIView.as_view(), name='Perform-Registration'),
    path('forgot/password/init', InitForgotPasswordAPIView.as_view(), name='Init-Forgot-Password'),
    path('forgot/password/perform', PerformForgotPasswordAPIView.as_view(), name='Perform-Forgot-Password'),
    path('password/change', ChangePasswordView.as_view(), name='User-Reset-Password'),

    path('recharge/compte', InitierPaiementAPIView.as_view(), name='Recharge-compte'),

    path('otp/init', InitPhoneOtpAPIView.as_view(), name='Init-Otp'),
    path('otp/perform', PerformOtpAPIView.as_view(), name='Perform-Otp'),

    path('moyens-paiement/', MoyenPaiementListCreateAPIView.as_view(), name='moyen-paiement-list-create'),
    path('moyens-paiement/<int:pk>/', MoyenPaiementDetailAPIView.as_view(), name='moyen-paiement-detail'),

    path('user/update/email/init', InitUpdateEmailAPIView.as_view(), name='Init-email-update'),
    path('user/update/email', UpdateEmailAPIView.as_view(), name='email-update'),

    path('user/update/phone/init', InitUpdatePhoneAPIView.as_view(), name='Init-phone-update'),
    path('user/update/phone', UpdatePhoneAPIView.as_view(), name='phone-update'),


]
