from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import *
from django.db import transaction
import stripe
from rest_framework import status
from bank_details.models import BankDetails, PaymentMethods
from users.utils import STRIPE_API_KEY, reponses

stripe.api_key = STRIPE_API_KEY


def saveBAnkDetails(user, payment_method_id) :
    try:
        stripe_payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        last4 = stripe_payment_method["card"]["last4"]
        provider = stripe_payment_method["card"]["brand"]
        exp_month = stripe_payment_method["card"]["exp_month"]
        exp_year = str(stripe_payment_method["card"]["exp_year"])[-2:]

        method = BankDetails.objects.create(
            user_id=user,
            last4=last4,
            provider=provider,
            expire_date=f"{exp_month:02}/{exp_year}",
            payment_method_id=payment_method_id
        )
        return {"message": "Méthode enregistrée"}, status.HTTP_201_CREATED

    except Exception as e:
        return {"error": str(e)}, status.HTTP_400_BAD_REQUEST

class ListPaymentMethodsBaseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_payment_methods(self, use_values):
        return PaymentMethods.objects.filter(use__in=use_values, active=True)

    def get(self, request, *args, **kwargs):
        use_type = kwargs.get("use_type")
        data = []
        if use_type == "in":
            user_bank_details = BankDetails.objects.filter(user_id=request.user.id)
            data += [{"name": str(userBank), "expire_date": userBank.expire_date} for userBank in user_bank_details]
        use_values = ["both", use_type] if use_type in ["in", "out"] else ["both"]

        payment_methods = self.get_payment_methods(use_values)
        data += [{"code": method.code, "name": method.name} for method in payment_methods]

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
        save_response = saveBAnkDetails(user, payment_method_id)

        return Response(save_response[0], status=save_response[1])

class ListBankDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        methods = BankDetails.objects.filter(user_id=user)
        data = [
            {
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
