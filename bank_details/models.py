from users.models import User
from django.db import models
from users.utils import encrypt_data, decrypt_data

USE_CHOICES = [("in", "Paiement"),
   ("out", "Retrait"),
    ("both", "Paiement et Retrait")]

class PaymentMethods(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    use = models.CharField(max_length=20, choices=USE_CHOICES)
    active = models.BooleanField()

    def __str__(self):
        return self.name

class BankDetails(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    last4 = models.CharField(max_length=4)
    provider = models.CharField(max_length=50, null=True, blank=True)
    expire_date = models.CharField(max_length=5, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    _payment_method_id = models.TextField(unique=True, null=True, blank=True)
    _customer_id = models.TextField(unique=True, null=True, blank=True)

    @property
    def customer_id(self):
        return decrypt_data(self._customer_id)

    @customer_id.setter
    def customer_id(self, value):
        self._customer_id = encrypt_data(value)

    @property
    def payment_method_id(self):
        return decrypt_data(self._payment_method_id)

    @payment_method_id.setter
    def payment_method_id(self, value):
        self._payment_method_id = encrypt_data(value)

    def __str__(self):
        return f"{self.provider} ****{self.last4}"