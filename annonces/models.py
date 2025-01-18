
from django.db import models

from commons.models import TimeStampedModel
from users.models import User


class Voyage(TimeStampedModel):
    date_depart = models.DateTimeField()
    provenance = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    agence_voyage = models.CharField(max_length=100)
    code_reservation = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Voyage'
        verbose_name_plural = 'Voyages'



class Annonce(TimeStampedModel):
    date_publication = models.DateTimeField(auto_now_add=True)
    est_publie = models.BooleanField(default=False)
    type_bagage_auto = models.CharField(max_length=100)
    nombre_kg_dispo = models.IntegerField()
    montant_par_kg = models.DecimalField(max_digits=10, decimal_places=2)
    cout_total = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    revenue_transporteur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    statut = models.CharField(max_length=50)
    est_actif = models.BooleanField(default=True)
    reference = models.CharField(max_length=50, unique=True)
    voyage = models.OneToOneField(Voyage, on_delete=models.CASCADE)
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annonces')


    class Meta:
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'
