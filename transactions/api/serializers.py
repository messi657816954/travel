from rest_framework import serializers
from transactions.models import Transactions
from annonces.api.serializers import AnnonceDetailSerializer
from users.api.serializers import UserDetailSerializer
from reservations.api.serializers import ReservationDetailsSerializer
from commons.api.serializers import CurrencySerializer


class TransactionSerializer(serializers.ModelSerializer):
    annonce_details = AnnonceDetailSerializer(source="announce", read_only=True)
    reservation_details = ReservationDetailsSerializer(source="reservation", read_only=True)
    currency_details = CurrencySerializer(source="currency", read_only=True)
    currency_to_collect_details = CurrencySerializer(source="currency_to_collect", read_only=True)
    sender_details = UserDetailSerializer(source='sender', read_only=True)
    beneficiary_details = UserDetailSerializer(source='beneficiary', read_only=True)
    class Meta:
        model = Transactions
        fields = '__all__'

    def validate(self, data):
        transaction_type = data.get('type')
        announce = data.get('announce')
        reservation = data.get('reservation')

        if transaction_type not in ['deposit', 'withdraw'] and (announce is None or reservation is None):
            raise serializers.ValidationError(
                "Announce and reservation cannot be null unless the transaction type is 'deposit' or 'withdraw'.")

        return data