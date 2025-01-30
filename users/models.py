from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Sum, Case, When, DecimalField, F, Q




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
    phone = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_phone_verify = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    # is_phone_verify = models.BooleanField(default=False)

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
        transactions = self.transactions_compte.all()  # Récupère les transactions liées au compte

        # Calcul de virtual_balance
        virtual_balance = transactions.aggregate(
            balance=Sum(
                Case(
                    # Ajouter les transactions de type DEPOSITE et CREDIT avec un statut différent de CANCEL
                    When(
                        Q(transaction_type__in=["DEPOSITE", "CREDIT"]) &
                        ~Q(transaction_status="CANCEL"),
                        then=F("montant")
                    ),
                    # Soustraire les transactions de type WITHDRAWAL et DEBIT avec un statut différent de CANCEL
                    When(
                        Q(transaction_type__in=["WITHDRAWAL", "DEBIT"]) &
                        ~Q(transaction_status="CANCEL"),
                        then=-F("montant")
                    ),
                    output_field=DecimalField()
                )
            )
        )['balance'] or 0  # Valeur par défaut si None

        # Calcul de real_balance
        real_balance = transactions.aggregate(
            balance=Sum(
                Case(
                    # Ajouter les transactions de type DEPOSITE et CREDIT avec un statut différent de SUCCESSFUL
                    When(
                        Q(transaction_type__in=["DEPOSITE", "CREDIT"]) &
                        ~Q(transaction_status="SUCCESSFUL"),
                        then=F("montant")
                    ),
                    # Soustraire les transactions de type WITHDRAWAL et DEBIT avec un statut différent de SUCCESSFUL
                    When(
                        Q(transaction_type__in=["WITHDRAWAL", "DEBIT"]) &
                        ~Q(transaction_status="SUCCESSFUL"),
                        then=-F("montant")
                    ),
                    output_field=DecimalField()
                )
            )
        )['balance'] or 0  # Valeur par défaut si None

        # Mettre à jour les champs du compte
        self.virtual_balance = virtual_balance
        self.real_balance = real_balance
        self.save()

        # Retourner les valeurs calculées
        return {
            "virtual_balance": virtual_balance,
            "real_balance": real_balance
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
