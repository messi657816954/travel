from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Sum, Case, When, DecimalField, F, Q, Avg, Count

from commons.models import Pays

class UserManager(BaseUserManager):

    def create_user(self, email, user_name, password,phone, **other_fields):

        if not email:
            raise ValueError("Provide email")
        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,phone=phone, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, user_name, password, **other_fields):
        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_superuser',True)
        other_fields.setdefault('is_active',True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('staff privilege must be assigned to superuser')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('superuser privilege must be assigned to superuser')

        return self.create_user(email, user_name, password,**other_fields)


class User(AbstractBaseUser,PermissionsMixin):

    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=100, unique=True)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_phone_verify = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)

    zip_code = models.CharField(max_length=100, null=True,blank=True)
    address = models.CharField(max_length=100, null=True,blank=True)
    city = models.CharField(max_length=100, null=True,blank=True)
    is_identity_check = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)


    REGISTRATION_CHOICES = [
        ('email', 'Email'),
        ('google', 'Google'),
    ]
    registration_method = models.CharField(
        max_length=10,
        choices=REGISTRATION_CHOICES,
        default='email'
    )
    reset_password_code = models.CharField(max_length=30,default="")

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']
    
    def __str__(self):
        return self.user_name

    def stats_notes_recues(self):
        """
        Calcule la moyenne des notes reçues et le nombre d'avis pour l'utilisateur.
        Returns:
            dict: Contient `moyenne` et `nombre_avis`.
        """
        stats = self.avis_recus.aggregate(
            moyenne=Avg('note'),
            nombre_avis=Count('id')
        )
        return {
            "moyenne": stats.get('moyenne', 0) or 0,
            "nombre_avis": stats.get('nombre_avis', 0)
        }

    def stats_reservations(self):
        from annonces.models import Reservation

        reservations_delivered = Reservation.objects.filter(
            annonce__in=self.annonces.all(),
            statut="DELIVERED"
        ).count()

        reservations_send = Reservation.objects.filter(
            user=self,
            statut="DELIVERED"
        ).count()

        return {
            "total_delivered": reservations_delivered,
            "total_send": reservations_send
        }


class UserEmails(models.Model):
    email = models.EmailField(null=True, blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True)



class MoyenPaiementUser(models.Model):
    type = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    numero_carte = models.CharField(max_length=16, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    cvv = models.CharField(max_length=4, null=True, blank=True)
    date_expiration = models.CharField(max_length=10, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)




class Compte(models.Model):
    virtual_balance = models.DecimalField(max_digits=10, decimal_places=2)
    real_balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def calculate_balances(self):
        """
        Calcule les virtual_balance et real_balance en fonction des transactions associées.
        """
        transactions = self.transactions_compte.all()

        balances = transactions.aggregate(
            # Calcul de virtual_balance
            virtual_balance=Sum(
                Case(
                    When(
                        Q(transaction_type="DEPOSITE") & ~Q(transaction_status="CANCEL"),
                        then=F("montant")
                    ),
                    When(
                        Q(transaction_type="CREDIT") & ~Q(transaction_status="CANCEL"),
                        then=F("montant")
                    ),
                    When(
                        Q(transaction_type="WITHDRAWAL") & ~Q(transaction_status="CANCEL"),
                        then=-F("montant")
                    ),
                    When(
                        Q(transaction_type="DEBIT") & ~Q(transaction_status="CANCEL"),
                        then=-F("montant")
                    ),
                    output_field=DecimalField()
                )
            ),

            # Calcul de real_balance
            real_balance=Sum(
                Case(
                    When(
                        Q(transaction_type="DEPOSITE") & ~Q(transaction_status="CANCEL"),
                        then=F("montant")
                    ),
                    When(
                        Q(transaction_type="CREDIT") & Q(transaction_status="SUCCESSFUL"),
                        then=F("montant")
                    ),
                    When(
                        Q(transaction_type="WITHDRAWAL") & ~Q(transaction_status="CANCEL"),
                        then=-F("montant")
                    ),
                    When(
                        Q(transaction_type="DEBIT") & Q(transaction_status="SUCCESSFUL"),
                        then=-F("montant")
                    ),
                    output_field=DecimalField()
                )
            )
        )

        # Mettre à jour les soldes en s'assurant qu'ils ne sont pas None
        self.virtual_balance = balances['virtual_balance'] or 0
        self.real_balance = balances['real_balance'] or 0
        self.save()

        return {
            "virtual_balance": self.virtual_balance,
            "real_balance": self.real_balance
        }



# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     titre = models.CharField(max_length=200)
#     message = models.TextField()
#     est_lu = models.BooleanField(default=False)
#     type = models.CharField(max_length=50)  # email, sms, in-app
#
#     class Meta:
#         verbose_name = 'Notification'
#         verbose_name_plural = 'Notifications'
