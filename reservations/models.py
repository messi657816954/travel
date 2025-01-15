

from django.db import models
from annonces.models import Annonce
from commons.models import TimeStampedModel

from users.models import User


REGISTRATION_CHOICES = [
        ('PENDING', 'PENDING'),
        ('google', 'Google'),
    ]

class Reservation(TimeStampedModel):
    nombre_kg = models.IntegerField()
    montant = models.DecimalField(max_digits=100, decimal_places=2)
    nom_personne_a_contacter = models.CharField(max_length=100)
    telephone_personne_a_contacter = models.CharField(max_length=20)
    code_livraison = models.CharField(max_length=50)
    reference = models.CharField(max_length=50, unique=True)
    date_paiement = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='reservations')

    statut = models.CharField(
        max_length=100,
        choices=REGISTRATION_CHOICES,
        default='PENDING'
    )

    class Meta:
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'



class Transaction(TimeStampedModel):
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=50)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'




