import random
import string
from django.conf import settings
import datetime

from django.core.mail import send_mail, EmailMessage
from twilio.rest import Client

import environ


env = environ.Env()
environ.Env.read_env()  # Read .env file

ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='AC2bb830ebf39487cae5db6c5af2ed8b0f')
AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='e2d9dfbafac110a43096310ce9b99675')
PHONE_NUMBER = env('TWILIO_PHONE_NUMBER', default='0000')


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
        email_to
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)

def send_otp(code, phone_to):

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        body=f"Ledjangui: Your Code is {code}. Do not share it with anyone.",
        from_=PHONE_NUMBER,
        to=phone_to
    )