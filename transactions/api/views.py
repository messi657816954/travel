from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
import stripe, requests, datetime
from django.conf import settings
from rest_framework import status

from preferences.models import UserPreference
from transactions.models import Transactions
from commons.models import Currency
from annonces.models import Reservation
from transactions.api.serializers import TransactionSerializer
from users.utils import reponses, SPRING_BOOT_UPDATE_PAYMENT_URL

def get_transaction_title(transaction, user_id):
    title = ""
    if transaction.sender == user_id:
        title += transaction.type == "fees" and "Frais d'annulation du" \
                 or transaction.type == "withdraw" and "Virement du" or "Payé le"
    else:
        title += transaction.state == "refund" and "Remboursé le" or transaction.state == "pending" and "En attente..." \
                 or transaction.type == "deposit" and "Recharge du" or "Payé le"

    title += transaction.created_at.strftime("%-d %b.")
    return title

def set_description(transaction):
    nb_kg = transaction.reservation.nombre_kg
    departure_date = transaction.announce.voyage.date_depart.strftime("%-d %B")
    departure = transaction.announce.voyage.provenance.intitule
    destination = transaction.announce.voyage.destination.intitule

    return departure_date + " " + str(nb_kg) + "Kg " + departure + " -> " + destination

def create_transactions(amount, currency, type, state, external_id=None, sender=None, beneficiary=None, reservation=None):
    transaction = Transactions.objects.create(
        type = type,
        state = state,
        amount = amount,
        amount_to_collect = amount,
        currency = currency,
        currency_to_collect = currency,
        announce = reservation and reservation.annonce,
        reservation = reservation,
        sender = sender,
        beneficiary = beneficiary,
        external_id = external_id
    )
    return transaction

def create_refund_transactions(transaction_id, amount, external_id):
    transaction_obj = Transactions.objects.get(pk=transaction_id)
    transaction_obj.pk = None
    transaction_obj.ref = None
    transaction_obj.beneficiary = transaction_obj.sender
    transaction_obj.sender = None
    transaction_obj.type = 'refund'
    transaction_obj.amount = amount
    transaction_obj.state = 'completed'
    transaction_obj.external_id = external_id
    return transaction_obj.save()

class TransactionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data["amount"]
        reservation_id = request.data["reservation"]
        payment_method_save = request.data.get("method_save")
        user_pref = UserPreference.objects.filter(user_id=request.user.id).first()
        currency = user_pref and user_pref.currency or Currency.objects.get(code='EUR')
        try:
            reservation = Reservation.objects.get(pk=reservation_id)
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Reservation not found'))
        transaction = create_transactions(amount, currency, "transfer", "pending", request.data["external_id"], request.user, reservation.annonce.user_id, reservation)
        reservation.date_paiement = datetime.datetime.now()
        reservation.save()
        try:
            params = {
                "processingId": request.data["external_id"],
                "transactionId": transaction.ref
            }
            response = requests.post(SPRING_BOOT_UPDATE_PAYMENT_URL, params=params, timeout=10)
        except requests.exceptions.RequestException:
            return Response(reponses(success=0, error_msg='Erreur de communication avec le service de paiement'), status=500)

        serializer = TransactionSerializer(transaction)
        return Response(reponses(success=1, results={'message': 'Transaction créée avec succès', 'data': serializer.data}))


class TransactionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            transaction_instance = Transactions.objects.get(pk=pk)
        except Transactions.DoesNotExist:
            return Response(reponses(success=0, error_msg='Transaction non trouvée'))

        serializer = TransactionSerializer(transaction_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(reponses(success=1, results={'message': 'Transaction mise à jour avec succès', 'data': serializer.data}))
        return Response(reponses(success=0, error_msg=str(serializer.errors)))


class ListUserTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        income_transactions = Transactions.objects.filter(beneficiary=user_id, state='completed').exclude(type='deposit')
        outcome_transactions = Transactions.objects.filter(sender=user_id).exclude(type='withdraw')
        all_transactions = income_transactions.union(outcome_transactions).order_by('-created_at')

        data = [
            {
                "name": transaction.state == 'failed' and "Transaction échoué" or get_transaction_title(transaction, user_id),
                "amount": transaction.sender == user_id and (-1) * transaction.amount or transaction.amount_to_collect,
                "description": transaction.state == 'failed' and "-" or set_description(transaction),
                "transport": transaction.announce.voyage.moyen_transport,
                "failed": transaction.state == 'failed'
            }
            for transaction in all_transactions
        ]
        return Response(reponses(success=1, results={'transactions': data}))


class ListUserPendingTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        transactions = Transactions.objects.filter(beneficiary=user_id, state='pending').order_by('-created_at')

        data = [
            {
                "name": get_transaction_title(transaction, user_id),
                "amount": transaction.amount_to_collect,
                "description": set_description(transaction),
                "transport": transaction.announce.voyage.moyen_transport,
                "failed": transaction.state == 'failed'
            }
            for transaction in transactions
        ]
        return Response(reponses(success=1, results={'pending_transactions': data}))


class ListUserAccountTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        income_transactions = Transactions.objects.filter(beneficiary=user_id, type='deposit')
        outcome_transactions = Transactions.objects.filter(sender=user_id, type='withdraw')
        all_transactions = income_transactions.union(outcome_transactions).order_by('-created_at')

        data = [
            {
                "name": get_transaction_title(transaction, user_id),
                "amount": transaction.sender == user_id and (-1) * transaction.amount or transaction.amount_to_collect,
                "description": "-",
                "transport": "-",
                "failed": transaction.state == 'failed'
            }
            for transaction in all_transactions
        ]
        return Response(reponses(success=1, results={'account_transactions': data}))


class UserBalanceAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        pending_transactions = Transactions.objects.filter(beneficiary=user_id, type='transfer', state='pending')
        in_transactions = Transactions.objects.filter(beneficiary=user_id, state='completed').exclude(type='refund')
        out_transactions = Transactions.objects.filter(sender=user_id, type__in=['fees', 'withdraw'])

        total_pending = sum([transaction.amount_to_collect for transaction in pending_transactions])
        total_in = sum([transaction.amount_to_collect for transaction in in_transactions])
        total_out = sum([transaction.amount for transaction in out_transactions])

        data = {
            "total_pending": total_pending,
            "pending_count": len(pending_transactions),
            "balance": total_in - total_out,
            "forecast": (total_in + total_pending) - total_out
        }
        return Response(reponses(success=1, results={'balance_info': data}))
