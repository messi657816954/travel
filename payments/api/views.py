import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from commons.models import Currency
from annonces.models import Reservation
from users.utils import reponses, SPRING_BOOT_PAYMENT_URL


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        currency_id = request.data.get("currency")
        reservation_id = request.data.get("reservation")
        payment_method = request.data.get("payment_method")

        try:
            currency = Currency.objects.get(pk=currency_id)
        except Currency.DoesNotExist:
            return Response(reponses(success=0, error_msg='Currency not found'), status=404)

        try:
            reservation = Reservation.objects.get(pk=reservation_id)
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Reservation not found'), status=404)

        payload = {
            "currency": currency.code,
            "amount": amount,
            "payment_method": payment_method
        }

        try:
            response = requests.post(SPRING_BOOT_PAYMENT_URL, json=payload, timeout=10)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                return Response(reponses(success=1, results={"clientSecret": response_data.get("clientSecret")}))
            else:
                return Response(reponses(success=0, error_msg='Échec du paiement'), status=400)

        except requests.exceptions.Timeout:
            return Response(reponses(success=0, error_msg='Le service de paiement est trop lent, veuillez réessayer.'), status=504)
        except requests.exceptions.RequestException:
            return Response(reponses(success=0, error_msg='Erreur de communication avec le service de paiement'), status=500)
