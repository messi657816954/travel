from users.models import User
from commons.models import Currency
from annonces.models import Annonce, Reservation
from django.db import models
from django.core.validators import MinValueValidator

TRANSACTIONS_STATE = [
    ('failed', 'Failed'),
    ('canceled', 'Canceled'),
    ('paid', 'Paid'),
    ("pendind", "Pending"),
    ("completed", "Completed")
]

TRANSACTIONS_TYPE = [
    ("deposit", "Deposit"),
    ("fees", "Fees"),
    ("transfer", "Transfer"),
    ("withdraw", "Withdraw"),
    ("refund", "Refund")
]

class Transactions(models.Model):
    ref = models.CharField(unique=True)
    type = models.CharField(choices=TRANSACTIONS_TYPE)
    state = models.CharField(choices=TRANSACTIONS_STATE)
    amount = models.DoubleField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0.01)])
    amount_to_collect = models.DoubleField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    announce = models.ForeignKey(Annonce, on_delete=models.CASCADE, null=True, blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    beneficiary = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)