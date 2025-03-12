from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
import stripe
from django.conf import settings
from rest_framework import status
from bank_details.models import BankDetails, PaymentMethods


class ListPaymentMethodsBaseView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_payment_methods(self, use_values):
        return PaymentMethods.objects.filter(use__in=use_values, active=True)

    def get(self, request, *args, **kwargs):
        use_type = kwargs.get("use_type")
        data = []
        if use_type == "in":
            user_bank_details = BankDetails.objects.filter(user_id=request.user.id)
            data += [{"code": userBank.id, "name": str(userBank)} for userBank in user_bank_details]
        use_values = ["both", use_type] if use_type in ["in", "out"] else ["both"]

        payment_methods = self.get_payment_methods(use_values)
        data += [{"code": method.code, "name": method.name} for method in payment_methods]

        return Response(data, status=status.HTTP_200_OK)

class ListPaymentMethodsView(ListPaymentMethodsBaseView):
    def get(self, request, *args, **kwargs):
        return super().get(request, use_type="in", *args, **kwargs)

class ListWithdrawMethodsView(ListPaymentMethodsBaseView):
    def get(self, request, *args, **kwargs):
        return super().get(request, use_type="out", *args, **kwargs)


class BankDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        user = request.user
        payment_method_id = request.data.get("payment_method_id")

        try:
            stripe_payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            last4 = stripe_payment_method["card"]["last4"]
            provider = stripe_payment_method["card"]["brand"]

            method = BankDetails.objects.create(
                user_id=user,
                last4=last4,
                provider=provider,
                payment_method_id=payment_method_id
            )
            return Response({"message": "Méthode enregistrée"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ListBankDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        methods = BankDetails.objects.filter(user_id=user)
        data = [
            {
                "name": method,
            }
            for method in methods
        ]
        return Response(data, status=status.HTTP_200_OK)

class DeleteBankDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk, *args, **kwargs):
        bank_detail = BankDetails.objects.get(id=pk)
        if not bank_detail:
            return Response({"message": "Coordonnées introuvable."}, status=status.HTTP_404_NOT_FOUND)
        bank_detail.delete()
        return Response({"message": "Coordonnées supprimé avec succès."}, status=status.HTTP_204_NO_CONTENT)
