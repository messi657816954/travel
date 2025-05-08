from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import *
from django.db import transaction
import stripe, requests
from rest_framework import status
from bank_details.models import BankDetails, PaymentMethods
from users.utils import STRIPE_API_KEY, reponses, SPRING_BOOT_BANK_ACCOUNT_URL

stripe.api_key = STRIPE_API_KEY


def saveBAnkDetails(user, payment_method_id, customer_id) :
    try:
        stripe_payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        last4 = stripe_payment_method["card"]["last4"]
        provider = stripe_payment_method["card"]["brand"]
        exp_month = stripe_payment_method["card"]["exp_month"]
        exp_year = str(stripe_payment_method["card"]["exp_year"])[-2:]

        method = BankDetails.objects.create(
            user_id=user,
            last4=last4,
            bank_type="card",
            provider=provider,
            expire_date=f"{exp_month:02}/{exp_year}",
            payment_method_id=payment_method_id,
            customer_id=customer_id
        )
        return {"message": "Méthode enregistrée"}, status.HTTP_201_CREATED

    except Exception as e:
        return {"error": str(e)}, status.HTTP_400_BAD_REQUEST

def saveBAnkAccountDetails(user, external_account_id, account_id) :
    try:
        stripe_bank_account = stripe.Account.retrieve_external_account(
            account_id,
            external_account_id
        )
        last4 = stripe_bank_account["last4"]
        provider = stripe_bank_account["bank_name"]

        method = BankDetails.objects.create(
            user_id=user,
            last4=last4,
            provider=provider,
            bank_type="bank_account",
            external_account_id=external_account_id,
            account_id=account_id
        )
        return {"message": "Bank account added"}, status.HTTP_201_CREATED

    except Exception as e:
        return {"error": str(e)}, status.HTTP_400_BAD_REQUEST

class ListPaymentMethodsBaseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_payment_methods(self, use_values):
        return PaymentMethods.objects.filter(use__in=use_values, active=True)

    def get(self, request, *args, **kwargs):
        use_type = kwargs.get("use_type")
        list_bank_details = []
        if use_type == "in":
            user_bank_details = BankDetails.objects.filter(user_id=request.user.id)
            list_bank_details = [{"payment_method_id": userBank.id, "provider": userBank.provider, "card_number": f"****{userBank.last4}", "expire_date": userBank.expire_date} for userBank in user_bank_details]
        use_values = ["both", use_type] if use_type in ["in", "out"] else ["both"]

        payment_methods = self.get_payment_methods(use_values)
        list_payment_methods = [{"code": method.code, "name": method.name} for method in payment_methods]
        data = {"list_bank_details": list_bank_details, "list_payment_methods": list_payment_methods}

        return Response(reponses(success=1, results=data), status=status.HTTP_200_OK)

class ListPaymentMethodsView(ListPaymentMethodsBaseView):
    def get(self, request, *args, **kwargs):
        return super().get(request, use_type="in", *args, **kwargs)

class ListWithdrawMethodsView(ListPaymentMethodsBaseView):
    def get(self, request, *args, **kwargs):
        return super().get(request, use_type="out", *args, **kwargs)


class BankDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        payment_method_id = request.data.get("payment_method_id")
        customer_id = request.data.get("customer_id")
        save_response = saveBAnkDetails(user, payment_method_id, customer_id)

        return Response(save_response[0], status=save_response[1])


class BankAccountDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        user_bank = BankDetails.objects.filter(user_id=request.user.id, bank_type="bank_account")
        payload = {}
        if len(user_bank) > 0:
            payload["connect_id"] = user_bank[0].account_id
        payload["country"] = request.data.get("country")
        payload["email"] = user.email
        payload["type"] = "express"
        payload["token_id"] = request.data.get("token_id")
        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if not auth_header.startswith("Bearer "):
                return Response({"detail": "Token manquant"}, status=401)

            response = requests.post(SPRING_BOOT_BANK_ACCOUNT_URL,
            headers={"Authorization": auth_header}, json=payload, timeout=10)
            response_data = response.json()

        except requests.exceptions.Timeout:
            return Response(reponses(success=0, error_msg='Service too slow try again.'), status=504)
        except requests.exceptions.RequestException:
            return Response(reponses(success=0, error_msg='Erreur de communication avec le service'), status=500)

        if response_data.get("status") == 200:
            account_id = response_data.get("data").get("account_id")
            external_id = response_data.get("data").get("external_account")
            save_response = saveBAnkAccountDetails(user, external_id, account_id)
            return Response(reponses(success=1, results=response_data))
        else:
            return Response(reponses(success=0, results=response_data), status=400)

class ListBankDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        methods = BankDetails.objects.filter(user_id=user)
        data = [
            {
                "payment_method_id": method.id,
                "provider": method.provider,
                "card_number": f"****{method.last4}",
                "expire_date": method.expire_date,
            }
            for method in methods
        ]
        return Response(reponses(success=1, results=data), status=status.HTTP_200_OK)

class DeleteBankDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        pk = request.query_params.get('pk')
        if not pk:
            return Response({"message": "Paramètre 'pk' manquant."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bank_detail = BankDetails.objects.get(id=pk)
        except BankDetails.DoesNotExist:
            return Response({"message": "Coordonnées introuvables."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id != bank_detail.user_id.id:
            return Response({"message": "Accès non autorisé."}, status=status.HTTP_403_FORBIDDEN)

        bank_detail.delete()
        return Response({"message": "Coordonnées supprimées avec succès."}, status=status.HTTP_200_OK)
