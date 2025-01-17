from datetime import timezone



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from reservations.api.serializers import ReservationSerializer
from reservations.models import Reservation
from users.utils import reponses, generate_reference
from .serializers import AnnonceSerializer, VoyageSerializer
#from commons.utils import reponses, generate_reference

from ..models import Annonce


class CreateAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # 1. Créer d'abord le voyage
            voyage_data = {
                'date_depart': request.data['date_depart'],
                'provenance': request.data['provenance'],
                'destination': request.data['destination'],
                'agence_voyage': request.data.get('agence_voyage', ''),
                'code_reservation': request.data.get('code_reservation', '')
            }

            voyage_serializer = VoyageSerializer(data=voyage_data)
            if not voyage_serializer.is_valid():
                return Response(reponses(
                    success=0,
                    error_msg='Données de voyage invalides',
                    errors=voyage_serializer.errors
                ))

            voyage = voyage_serializer.save()

            # 2. Créer ensuite l'annonce
            montant_par_kg = Decimal(request.data['montant_par_kg'])
            nombre_kg = Decimal(request.data['nombre_kg_dispo'])
            cout_total = montant_par_kg * nombre_kg
            # commission = cout_total * Decimal('0.10')  # 10% de commission

            annonce_data = {
                'date_publication': timezone.now(),
                'est_publie': False,
                'type_bagage_auto': request.data['type_bagage_auto'],
                'nombre_kg_dispo': nombre_kg,
                'montant_par_kg': montant_par_kg,
                'cout_total': cout_total,
                # 'commission': commission,
                # 'revenue_transporteur': cout_total - commission,
                'statut': 'ACTIF',
                'est_actif': True,
                'reference': generate_reference(),
                'voyage': voyage.id,
                'createur': request.user.id
            }

            annonce_serializer = AnnonceSerializer(data=annonce_data)
            if not annonce_serializer.is_valid():
                return Response(reponses(
                    success=0,
                    error_msg='Données d\'annonce invalides',
                    errors=annonce_serializer.errors
                ))

            annonce = annonce_serializer.save()

            # 3. Préparer la réponse avec les données combinées
            response_data = {
                **annonce_serializer.data,
                'voyage': voyage_serializer.data
            }

            return Response(reponses(success=1, results=response_data))

        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



    def _notifier_creation_annonce(self, annonce):
        """Envoie une notification de confirmation de création d'annonce"""
        ctx = {
            'reference': annonce.reference,
            'provenance': annonce.voyage.provenance,
            'destination': annonce.voyage.destination,
            'date_depart': annonce.voyage.date_depart,
            'kg_disponibles': annonce.nombre_kg_dispo,
            'montant_par_kg': annonce.montant_par_kg
        }

        message = render_to_string('creation_annonce.html', ctx)
        mail = EmailMessage(
            "Confirmation de création d'annonce",
            message,
            settings.EMAIL_HOST_USER,
            [annonce.createur.email]
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)



class ReserverKilogrammesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            annonce = Annonce.objects.get(id=request.data['annonce_id'])

            if annonce.nombre_kg_dispo < int(request.data['nombre_kg']):
                return Response(reponses(success=0, error_msg='Kilogrammes demandés non disponibles'))

            # Créer la réservation
            reservation_data = {
                'nombre_kg': request.data['nombre_kg'],
                'montant': Decimal(request.data['nombre_kg']) * annonce.montant_par_kg,
                'nom_personne_a_contacter': request.data['nom_destinataire'],
                'telephone_personne_a_contacter': request.data['telephone_destinataire'],
                'statut': 'EN_ATTENTE',
                'reference': generate_reference(),
                'user': request.user.id,
                'annonce': request.data['annonce_id']
            }

            serializer = ReservationSerializer(data=reservation_data)
            if not serializer.is_valid():
                return Response(reponses(success=0, error_msg=serializer.errors))
            reservation = serializer.save()
            # Mettre à jour les kg disponibles
            annonce.nombre_kg_dispo -= int(request.data['nombre_kg'])
            annonce.save()

            return Response(reponses(success=1, results=serializer.data))

        except Annonce.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


    def _notifier_annonceur(self, annonce, reservation):
        ctx = {
            'annonce_ref': annonce.reference,
            'reservation_ref': reservation.reference,
            'kg_reserves': reservation.nombre_kg
        }
        message = render_to_string('nouvelle_reservation.html', ctx)
        mail = EmailMessage(
            "Nouvelle réservation",
            message,
            settings.EMAIL_HOST_USER,
            [annonce.createur.email]
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)


import asyncio
from asgiref.sync import sync_to_async

async def send_email_async(subject, message, recipient_email):
    mail = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [recipient_email],
    )
    mail.content_subtype = "html"
    await sync_to_async(mail.send)(fail_silently=True)


class ConfirmerReceptionColisAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(id=reservation_id)

            # Vérifier que c'est bien l'annonceur qui confirme
            if request.user != reservation.annonce.createur:
                return Response(reponses(success=0, error_msg="Non autorisé: c'est l'annonceur qui doit confirmer"))

            # Générer et envoyer le code de confirmation au destinataire
            code_livraison = generate_reference()

            # Mettre à jour le statut de la réservation
            reservation.statut = 'CONFIRM'
            reservation.code_livraison = code_livraison
            reservation.save()

            # apres le paiement il faut mettre à jour le compte du client et faire la transaction

            # Préparer le contexte de l'email
            ctx = {
                'code_confirmation': code_livraison
            }
            message = render_to_string('confirm_reception_colis.html', ctx)
            # Envoyer l'email de manière asynchrone
            asyncio.create_task(send_email_async("Code de confirmation de réception", message, reservation.user.email))

            return Response(reponses(success=1, results={'message': 'Code de confirmation envoyé'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))














class ConfirmerLivraisonAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, reservation_id):
        try:
            code_confirmation = request.data.get('code_confirmation')
            reservation = Reservation.objects.get(id=reservation_id)

            # Vérifier le code de confirmation
            if code_confirmation != reservation.code_livraison:
                return Response(reponses(success=0, error_msg='Code de confirmation invalide'))

            # Finaliser la livraison
            reservation.statut = 'DELIVRATE'
            reservation.save()
            annonce = Annonce.objects.get(id=reservation.annonce.pk)
            annonce.est_actif = False
            annonce.save()
            # TODO: apres le paiement il faut mettre à jour le compte de l'annonceur et faire la transaction

            # Notifier toutes les parties
            ctx = {
                'reservation_ref': reservation.reference
            }
            message = render_to_string('confirm_livraison_colis.html', ctx)
            asyncio.create_task(send_email_async("Livraison du colis", message, reservation.user.email))

            return Response(reponses(success=1, results={'message': 'Livraison confirmée avec succès'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


