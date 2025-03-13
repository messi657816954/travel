from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
import stripe
from django.conf import settings
from rest_framework import status
from transactions.models import Transactions


def get_transaction_title(transaction, user_id):
    title = ""
    if transaction.sender == user_id:
        title += transaction.type == "fees" and "Frais d'annulation du" \
                 or transaction.type == "withdraw" and "Virement du" or "Payé le"
    else:
        title += transaction.state == "refund" and "Remboursé le" or transaction.state == "pending" and "En attente..." \
                 or transaction.type == "deposit" and "Recharge du" or "Payé le"

    title += transaction.created_at.strtime("%-d %b.")
    return title

def set_description(transaction):
    nb_kg = transaction.reservation.nombre_kg
    departure_date = transaction.announce.voyage.date_depart.strtime("%-d %B")
    departure = transaction.announce.voyage.provenance.intitule
    destination = transaction.announce.voyage.destination.intitule

    return departure_date + " " + nb_kg + "Kg " + departure + " -> " + destination


class ListUserTransactionsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        income_transactions = Transactions.objects.filter(beneficiary=user_id, state__in=['completed', 'refund'])
        outcome_transactions = Transactions.objects.filter(sender=user_id).exclude(state='failed')
        all_transactions = income_transactions.union(outcome_transactions).order_by('-created_at')

        data = [
            {
                "name": get_transaction_title(transaction, user_id),
                "amount": transaction.sender == user_id and (-1) * transaction.amount or transaction.amount_to_collect,
                "description": set_description(transaction),
                "transport" : transaction.announce.voyage.moyen_transport
            }
            for transaction in all_transactions
        ]
        return Response(data, status=status.HTTP_200_OK)
