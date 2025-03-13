from rest_framework import serializers
from transactions.models import Transactions


class TransactionSerializer(serializers.ModelSerializer):
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