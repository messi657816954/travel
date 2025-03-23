import random
import string
from django.conf import settings
import datetime

from django.core.mail import send_mail, EmailMessage
from twilio.rest import Client

from cryptography.fernet import Fernet

import environ


env = environ.Env()
environ.Env.read_env()  # Read .env file

ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='AC2bb830ebf39487cae5db6c5af2ed8b0f')
AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='e2d9dfbafac110a43096310ce9b99675')
PHONE_NUMBER = env('TWILIO_PHONE_NUMBER', default='0000')
ENCRYPTION_KEY = env('ENCRYPTION_KEY', default='gR8dKj9_mN7pQ2vL5xYcT0wF4uB3eA1iZ6tH8sJ9kO0=')
STRIPE_API_KEY = env('STRIPE_API_KEY', default='TaCleSuperSecurisee1234567890=')
SPRING_BOOT_PAYMENT_URL = env('SPRING_BOOT_PAYMENT_URL', default='http://localhost:8084/api/payment/create-payment-intent')
SPRING_BOOT_UPDATE_PAYMENT_URL = env('SPRING_BOOT_UPDATE_PAYMENT_URL', default='http://localhost:8084/api/payment/confirm-payment')
SPRING_BOOT_REFUND_PAYMENT_URL = env('SPRING_BOOT_REFUND_PAYMENT_URL', default='http://localhost:8084/api/payment/refund-payment')


ROLES = (
    ('MANAGER', 'MANAGER'),
    ('CLIENT', 'CLIENT'),
    ('ADMIN', 'ADMINISTRATEUR'),
    ('PAYEUR', 'PAYEUR'),
)

TYPE_OP = (
    ('CONNEXION', 'CONNEXION'),
    ('DECONNEXION', 'DECONNEXION'),
    # ('APPELFONDS', 'APPELS DE FONDS'),
    # ('PAIEMENTFACTURE', 'PAIEMENT DE FACTURE ENEO'),
    # ('CANALSAT', 'PAIEMENT DE FACTURE CANALSAT'),
    # ('CHANGEPASSWORD', 'CHANGE PASSWORD'),
    ('CREATED', 'CREATION'),
)

STATUT = (
    ('CANCEL', 'CANCEL'),
    ('REJETER', 'REJETER'),
    ('PROGRESS', 'PROGRESS'),
    ('WAIT', 'WAIT'),
    ('FINISH', 'FINISH'),
    ('SUCCESS', 'SUCCESS'),
)

TYPE_PLAFOND = (
    ('DECOUVERT', 'DECOUVERT'),
    ('APPELFONDS', 'APPELS DE FONDS'),
    ('PAIEMENTFACTURE', 'PAIEMENT DE FACTURE ENEO'),
    ('CANALSAT', 'PAIEMENT DE FACTURE CANALSAT'),
)

STATUS_DECOUVERT = (
    ('TRUE', 'TRUE'),
    ('FALSE', 'FALSE'),
)

STATUT_SOUSCRIPTION = (
    ('ACTIVE', 'ACTIVE'),
    ('DEACTIVE', 'DEACTIVE'),
)

USER = 'USER'
BANK = 'BANK'
TYPE = (
    ('USER', 'USER'),
    ('BANK', 'BANK'),
)

TYPE_OPERATION = (
    ('APPELFONDS', 'APPELS DE FONDS'),

    ('DECOUVERT', 'DECOUVERT'),

    ('PAIEMENTFACTURE', 'PAIEMENT DE FACTURE ENEO'),
    ('CANAL', 'PAIEMENT DE FACTURE CANALSAT'),
    ('CAMWATER', 'PAIEMENT DE FACTURE CAMWATER'),
    ('ENEOPOSTPAY', 'PAIEMENT DE FACTURE ENEO APRES CONSOMMATION'),
    ('ENEOPREPAY', 'PAIEMENT DE FACTURE ENEO AVANT CONSOMMATION'),
    ('UDS', 'PAIEMENT DE UNIVERSITE DE DSCHANG'),

    ('MTN_MOBILEMONEY_CM', 'TRANSFERT MOMO'),
    ('ORANGE_MONEY_CM', 'TRANSFERT OM'),
    ('EXPRESS_UNION_MOBILEMONEY', 'TRANSFERT EXPRESS UNION'),
    ('AFRIKPAY', 'TRANSFERT AFRIKPAY'),
    ('AIRTIME', 'ACHAT DE CREDIT AIRTIME'),

    ('VERSEMNTAGENT', 'VERSEMENTS AGENT BANCAIRE'),
    ('RETRAITAGENT', 'RETRAIT AGENT BANCAIRE'),
    
)
SENS = (
    ('IN', 'IN'),
    ('OUT', 'OUT'),
    ('CREDIT', 'CREDIT'),
    ('', ''),
)
OPERATOR = (
    ('CAMTEL', 'CAMTEL'),
    ('MTN', 'MTN'),
    ('ORANGE', 'ORANGE'),
    ('NEXTTEL', 'NEXTTEL'),
    ('YOOMEE', 'YOOMEE'),
)


ETAT_DEMANDE_CHEQUE = (
    ('S', 'ETAT_DEMANDE_SAISIE'),
    ('A', 'ETAT_DEMANDE_ACCORDER'),
    ('T', 'ETAT_DEMANDE_TRAITEMENT'),
    ('R', 'ETAT_DEMANDE_REJETER'),
    ('E', 'ETAT_DEMANDE_EN_ATTENTE'),
    ('N', 'ETAT_DEMANDE_ANNULEE'),
)

NOMBRE_FEUILLET = (
    ('25', '25'),
    ('50', '50'),
    ('100', '100'),
)

ETAT_COMPTE = (
    ('A', 'ACTIF'),
    ('I', 'INACTIF'),
    ('B', 'BLOQUE'),
    ('D', 'BLOQUE_DEBIT'),
    ('C', 'BLOQUE_CREDIT'),
    ('L', 'CLOTURER'),
    ('O', 'DORMANT'),
    ('X', 'DOUTEUX'),
    ('N', 'NORMAL'),
)

ETAT_CHEQUE = (
    ('I', 'CHEQUE EN STOCK'),
    ('C', 'CHEQUE CLIENT'),
    ('G', 'CHEQUE GUICHET'),
    ('B', 'CHEQUE BLOQUER'),
    ('P', 'CHEQUE PAYE'),
)

LIBELLE_PARAMETRE_SUIVIS_SOLDE = (
    ('E', 'ENSOLEILLE'),
    ('N', 'NUAGEUX'),
    ('P', 'PLUVIEUX'),
    ('V', 'VENTEUX'),
    ('N', 'NEIGEUX')
)
API_MSG_CODE_CREAT_BANK = 'MG022'



def reponses(success, num_page=None, results=None, error_msg=None):
    RESPONSE_MSG = [
        {
            'success': success,

        }
    ]

    if num_page:
        RESPONSE_MSG[0].update(
            {'nombre_page': num_page}
        )
    if results:
        if isinstance(results, list):
            RESPONSE_MSG[0].update(
                {'results': results}
            )
        else:
            RESPONSE_MSG[0].update(
                {'results': [results]}
            )
    if error_msg :
        RESPONSE_MSG[0].update(
            {'errors': [{'error_msg': error_msg}]}
        )

    return RESPONSE_MSG


def generate_password(stringLength=6):
    # lettre = string.ascii_lowercase
    # return ''.join(random.choice(lettre) for i in range(stringLength))
    return ''.join(str(random.randrange(10)) for i in range(6))


def logger(request, message):
    # try:
    fichier = open(settings.BASE_DIR + '/log/debug.log', "w")
    fichier.write("Date " + str(datetime.datetime.now()) + 
    "/ Requete de " + str(request.META['REMOTE_ADDR']) +
    '/' + str(message) + str(request.META['HTTP_HOST']) +
    '/ Methode ' + str(request.META['REQUEST_METHOD']) + 
    '/ A la bd ' + str(settings.DATABASES['default']['NAME']) + 
    '/ Port ' + str(settings.DATABASES['default']['PORT']) + 
    '/ Sur ' + str(settings.DATABASES['default']['HOST']) +'\n')
    fichier.close()
    # except IOError:
    #     pass
    return True



import uuid
import datetime

def generate_reference():
    """
    Génère une chaîne unique pour représenter une référence.
    Format : YYYYMMDDHHMMSS-UUID
    """
    # Obtenir l'horodatage actuel
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # Générer un UUID unique
    unique_id = uuid.uuid4().hex[:8]  # Utiliser les 8 premiers caractères de l'UUID

    # Combiner l'horodatage et l'UUID
    reference = f"{timestamp}-{unique_id}"

    return reference


def send_email(object, body, email_to):

    mail = EmailMessage(
        object,
        body,
        settings.EMAIL_HOST_USER,
        [email_to]
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)

def send_otp(code, phone_to):

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=f"Lejangui: Your Code is {code}. Do not share it with anyone.",
        from_=PHONE_NUMBER,
        to=phone_to
    )

fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data: str) -> str:
    return fernet.decrypt(data.encode()).decode()






from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from twilio.rest import Client
from django.core.exceptions import ObjectDoesNotExist



def notify_user(user, subject, template_name=None, context=None, plain_message=None):
    """
    Notifie un utilisateur selon ses préférences de communication, avec email par défaut si 'none'.

    Args:
        user (User): L'utilisateur à notifier.
        subject (str): Sujet de la notification (utilisé pour email).
        template_name (str, optional): Nom du template HTML pour email.
        context (dict, optional): Contexte pour rendre le template email.
        plain_message (str, optional): Message texte brut pour SMS ou fallback.
    """
    try:
        preferences = user.preferences  # Récupérer les préférences
        communication_method = preferences.communication
    except ObjectDoesNotExist:
        communication_method = 'email'  # Par défaut si pas de préférences

    if communication_method in ['email', 'none'] and template_name and context:
        # Notification par email (par défaut pour 'none')
        message = render_to_string(template_name, context)
        mail = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)

    elif communication_method == 'sms' and plain_message:
        # Notification par SMS
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(
            body=plain_message,
            from_=PHONE_NUMBER,
            to=user.phone
        )

    else:
        # Cas de fallback ou erreur
        if communication_method == 'email' and not (template_name and context):
            raise ValueError("Pour email, template_name et context sont requis")
        if communication_method == 'sms' and not plain_message:
            raise ValueError("Pour SMS, plain_message est requis")



