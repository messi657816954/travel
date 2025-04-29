import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from bank_details.models import BankDetails
from annonces.models import Reservation
from users.utils import reponses, SPRING_BOOT_PAYMENT_URL, SPRING_BOOT_SETUP_PAYMENT_URL, SPRING_BOOT_PAYMENT_WITH_SAVED_CARD_URL
from preferences.models import UserPreference


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        reservation_id = request.data.get("reservation")
        payment_method = request.data.get("payment_method")
        user_pref = UserPreference.objects.filter(user_id=request.user.id).first()
        currency_code = user_pref and user_pref.currency.code or 'EUR'

        try:
            reservation = Reservation.objects.get(pk=reservation_id)
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Reservation not found'), status=404)

        payload = {
            "currency": currency_code,
            "amount": amount,
            "payment_method": payment_method
        }

        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Token manquant"}, status=401)

            response = requests.post(SPRING_BOOT_PAYMENT_URL,
            headers={"Authorization": auth_header}, json=payload, timeout=10)
            response_data = response.json()

            if response_data.get("status") == 200:
                return Response(reponses(success=1, results=response_data))
            else:
                return Response(reponses(success=0, error_msg='Échec du paiement'), status=400)

        except requests.exceptions.Timeout:
            return Response(reponses(success=0, error_msg='Le service de paiement est trop lent, veuillez réessayer.'), status=504)
        except requests.exceptions.RequestException:
            return Response(reponses(success=0, error_msg='Erreur de communication avec le service de paiement'), status=500)




class PaymentWithSavedCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        reservation_id = request.data.get("reservation")
        payment_method = request.data.get("payment_method")
        payment_method_id = request.data.get("payment_method_id")
        customer_id = request.data.get("customer_id")
        user_pref = UserPreference.objects.filter(user_id=request.user.id).first()
        currency_code = user_pref and user_pref.currency.code or 'EUR'

        try:
            reservation = Reservation.objects.get(pk=reservation_id)
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Reservation not found'), status=404)

        payload = {
            "currency": currency_code,
            "amount": amount,
            "paymentMethod": payment_method,
            "paymentMethodId": payment_method_id,
            "customerId": customer_id
        }

        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Token manquant"}, status=401)

            response = requests.post(SPRING_BOOT_PAYMENT_WITH_SAVED_CARD_URL,
            headers={"Authorization": auth_header}, json=payload, timeout=10)
            response_data = response.json()

            if response_data.get("status") == 200:
                return Response(reponses(success=1, results=response_data))
            else:
                return Response(reponses(success=0, error_msg='Échec du paiement'), status=400)

        except requests.exceptions.Timeout:
            return Response(reponses(success=0, error_msg='Le service de paiement est trop lent, veuillez réessayer.'), status=504)
        except requests.exceptions.RequestException:
            return Response(reponses(success=0, error_msg='Erreur de communication avec le service de paiement'), status=500)


class SetupIntendPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        bank_details = BankDetails.objects.filter(user_id=user).exclude(_customer_id=None)
        if len(bank_details) > 0:
            payload = {
                "customer_id": bank_details[0].customer_id
            }
        else:
            payload = {
                "last_name": user.lastname,
                "email": user.email
            }
        payload["type"] = request.data["payment_method"]

        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Token manquant"}, status=401)

            response = requests.post(SPRING_BOOT_SETUP_PAYMENT_URL,
            headers={"Authorization": auth_header}, json=payload, timeout=10)
            response_data = response.json()

            if response_data.get("status") == 200:
                return Response(reponses(success=1, results={"client_secret":response_data.get("data")}))
            else:
                return Response(reponses(success=0, error_msg='Échec du paiement'), status=400)

        except requests.exceptions.Timeout:
            return Response(reponses(success=0, error_msg='Le service de paiement est trop lent, veuillez réessayer.'),
                            status=504)
        except requests.exceptions.RequestException:
            return Response(reponses(success=0, error_msg='Erreur de communication avec le service de paiement'),
                            status=500)