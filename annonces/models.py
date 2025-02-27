from django.core.exceptions import ValidationError
from django.db import models

from commons.models import TimeStampedModel, Ville, TypeBagage
from users.models import User, Compte

TRANSPORT_CHOICES = [
        ('AERIEN', 'AERIEN'),
        ('FERROVIAIRE', 'FERROVIAIRE'),
        ('ROUTIER', 'ROUTIER'),
        ('MARITIME', 'MARITIME'),
    ]


class Voyage(TimeStampedModel):
    date_depart = models.DateTimeField()
    provenance = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='villes_prov')
    destination = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='villes_dest')
    agence_voyage = models.CharField(max_length=100)
    code_reservation = models.CharField(max_length=100)
    moyen_transport = models.CharField(
        max_length=100,
        choices=TRANSPORT_CHOICES,
        default=''
    )

    class Meta:
        verbose_name = 'Voyage'
        verbose_name_plural = 'Voyages'



class Annonce(TimeStampedModel):
    date_publication = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    # type_bagage_auto = models.CharField(max_length=100)
    nombre_kg_dispo = models.IntegerField()
    montant_par_kg = models.DecimalField(max_digits=10, decimal_places=2)
    cout_total = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    revenue_transporteur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # statut = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    reference = models.CharField(max_length=50, unique=True)
    voyage = models.OneToOneField(Voyage, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annonces')
    # type_bagage_auto = models.ForeignKey(TypeBagage, on_delete=models.CASCADE, related_name='annonces_bagage')



    class Meta:
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'


class TypeBagageAnnonce(models.Model):
    type_bagage = models.ForeignKey(TypeBagage, on_delete=models.CASCADE, related_name='type_bagage_annonces')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='bagage_annonces')






RESERVATION_STATUS = [
        ('PENDING', 'PENDING'),
        ('VALIDATE', 'VALIDATE'),
        ('CONFIRM', 'CONFIRM'),
        ('RECEPTION', 'RECEPTION'),
        ('DELIVRATE', 'DELIVRATE'),
        ('CANCEL', 'CANCEL'),
    ]


class Reservation(TimeStampedModel):
    nombre_kg = models.IntegerField()
    montant = models.DecimalField(max_digits=100, decimal_places=2)
    nom_personne_a_contacter = models.CharField(max_length=100)
    telephone_personne_a_contacter = models.CharField(max_length=20)
    code_livraison = models.CharField(max_length=50, unique=True, null=True, blank=True)
    code_reception = models.CharField(max_length=50, unique=True, null=True, blank=True)
    reference = models.CharField(max_length=50, unique=True)
    date_paiement = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations_user')
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='reservations_annonce')
    # type_bagage = models.ForeignKey(TypeBagage, on_delete=models.CASCADE, related_name='reservations_bagage')
    description = models.TextField(max_length=300)

    statut = models.CharField(
        max_length=100,
        choices=RESERVATION_STATUS,
        default='PENDING'
    )

    class Meta:
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'



class TypeBagageReservation(models.Model):
    type_bagage = models.ForeignKey(TypeBagage, on_delete=models.CASCADE, related_name='type_bagage_reservations')
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='bagage_reservations')



class Paiement(models.Model):
    # type = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    numero_carte = models.CharField(max_length=16, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    cvv = models.CharField(max_length=4, null=True, blank=True)
    date_expiration = models.CharField(max_length=10, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=100, decimal_places=2)
    STATUS_TYPE = [
        ('PENDING', 'PENDING'),
        ('SUCCESSFUL', 'SUCCESSFUL'),
        ('FAILED', 'FAILED'),
    ]
    status = models.CharField(
        max_length=12,
        choices=STATUS_TYPE,
        default=''
    )
    PAIEMENT_TYPE = [
        ('MOBILE', 'MOBILE'),
        ('BANQUE', 'BANQUE'),
    ]
    type = models.CharField(
        max_length=12,
        choices=PAIEMENT_TYPE,
        default=''
    )


    # type_paiement = models.CharField(
    #     max_length=12,
    #     choices=PAIEMENT_TYPE,
    #     default=''
    # )


class Transaction(TimeStampedModel):
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='transactions_reservation',null=True,blank=True)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='transactions_compte')
    TRANSACTION_TYPE = [
        ('DEPOSITE', 'DEPOSITE'),
        ('WITHDRAWAL', 'WITHDRAWAL'),
        ('DEBIT', 'DEBIT'),
        ('CREDIT', 'CREDIT'),
    ]
    transaction_type = models.CharField(
        max_length=12,
        choices=TRANSACTION_TYPE,
        default=''
    )
    TRANSACTION_STATUS = [
        ('PENDING', 'PENDING'),
        ('SUCCESSFUL', 'SUCCESSFUL'),
        ('CANCEL', 'CANCEL'),
    ]
    transaction_status = models.CharField(
        max_length=12,
        choices=TRANSACTION_STATUS,
        default=''
    )


    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'




class AvisUser(models.Model):
    NOTE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    note = models.IntegerField(choices=NOTE_CHOICES)
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    utilisateur_auteur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="avis_donnes"
    )
    utilisateur_note = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="avis_recus"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="avis_reservations",
        blank=True, null=True
    )
    annonce = models.ForeignKey(
        Annonce, on_delete=models.CASCADE, related_name="avis_annonces",
        blank=True, null=True
    )

    class Meta:
        # Ensure we can't have duplicates for the same author/user combination on a reservation
        # or duplicates for the same author/user combination on an announcement
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(reservation__isnull=False, annonce__isnull=True) |
                    models.Q(reservation__isnull=True, annonce__isnull=False)
                ),
                name='one_relation_only'
            ),
            models.UniqueConstraint(
                fields=['utilisateur_auteur', 'utilisateur_note', 'reservation'],
                name='unique_avis_reservation',
                condition=models.Q(reservation__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['utilisateur_auteur', 'utilisateur_note', 'annonce'],
                name='unique_avis_annonce',
                condition=models.Q(annonce__isnull=False)
            )
        ]


    def save(self, *args, **kwargs):
        # Ensure we have exactly one relation - either reservation or annonce, not both
        if (self.reservation is None and self.annonce is None) or (self.reservation is not None and self.annonce is not None):
            raise ValidationError("Un avis doit être lié soit à une réservation, soit à une annonce, mais pas les deux.")
        super().save(*args, **kwargs)

