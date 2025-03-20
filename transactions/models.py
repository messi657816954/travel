from users.models import User
from commons.models import Currency
from annonces.models import Annonce, Reservation
from django.db import models
from django.core.validators import MinValueValidator
import uuid

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
    ref = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    type = models.CharField(max_length=20, choices=TRANSACTIONS_TYPE)  # Ajout de max_length
    state = models.CharField(max_length=20, choices=TRANSACTIONS_STATE)  # Ajout de max_length
    externa_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.01)]
    )
    amount_to_collect = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)]  # Permet 0 pour amount_to_collect
    )
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    announce = models.ForeignKey(
        Annonce,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions'  # Ajout de related_name
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions'  # Ajout de related_name
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sent_transactions'  # Ajout de related_name
    )
    beneficiary = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_transactions'  # Ajout de related_name
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transaction'  # Nom au singulier
        verbose_name_plural = 'Transactions'  # Nom au pluriel
        ordering = ['-created_at']  # Tri par défaut par date de création décroissante

    def __str__(self):
        return f"Transaction {self.ref} - {self.type} ({self.state})"
