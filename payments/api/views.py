import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from bank_details.models import BankDetails
from annonces.models import Reservation
from users.utils import (reponses,
                         SPRING_BOOT_PAYMENT_URL,
                         SPRING_BOOT_SETUP_PAYMENT_URL,
                         SPRING_BOOT_PAYMENT_WITH_SAVED_CARD_URL,
                         SPRING_BOOT_WITHDRAW_URL)
from preferences.models import UserPreference


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method")
        payment_type = request.query_params.get('payment_type', None)
        user_pref = UserPreference.objects.filter(user_id=request.user.id).first()
        currency_code = user_pref and user_pref.currency.code or 'EUR'

        if payment_type is None:
            reservation_id = request.data.get("reservation")
            try:
                reservation = Reservation.objects.get(pk=reservation_id, user=request.user)
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
        payment_method = request.data.get("payment_method")
        payment_method_id = request.data.get("payment_method_id")
        payment_type = request.query_params.get('payment_type', None)
        user_pref = UserPreference.objects.filter(user_id=request.user.id).first()
        currency_code = user_pref and user_pref.currency.code or 'EUR'

        try:
            bank_detail = BankDetails.objects.get(pk=payment_method_id, user_id=request.user.id)
        except BankDetails.DoesNotExist:
            return Response(reponses(success=0, error_msg='Payment method not found'), status=404)

        if payment_type is None:
            reservation_id = request.data.get("reservation")
            try:
                reservation = Reservation.objects.get(pk=reservation_id, user=request.user)
            except Reservation.DoesNotExist:
                return Response(reponses(success=0, error_msg='Reservation not found'), status=404)
        elif payment_type not in ('deposit', 'withdraw'):
            return Response(reponses(success=0, error_msg='Invalid params'), status=400)

        payload = {
            "currency": currency_code,
            "amount": amount,
            "paymentMethod": payment_method,
            "paymentMethodId": bank_detail.payment_method_id,
            "customerId": bank_detail.customer_id
        }

        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Token manquant"}, status=401)

            url = (payment_type is None or payment_type == "deposit") and SPRING_BOOT_PAYMENT_WITH_SAVED_CARD_URL or SPRING_BOOT_WITHDRAW_URL
            response = requests.post(url, headers={"Authorization": auth_header},
                                     json=payload, timeout=10)
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

            print(payload)

            response = requests.post(SPRING_BOOT_SETUP_PAYMENT_URL,
            headers={"Authorization": auth_header}, json=payload, timeout=10)
            response_data = response.json()

            if response_data.get("status") == 200:
                return Response(reponses(success=1, results=response_data))
            else:
                return Response(reponses(success=0, error_msg='Échec du paiement'), status=400)

        except requests.exceptions.Timeout:
            return Response(reponses(success=0, error_msg='Le service de paiement est trop lent, veuillez réessayer.'),
                            status=504)
        except requests.exceptions.RequestException:
            return Response(reponses(success=0, error_msg='Erreur de communication avec le service de paiement'),
                            status=500)