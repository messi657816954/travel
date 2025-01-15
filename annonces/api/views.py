from datetime import timezone



from .models import Annonce, Reservation
from .serializers import AnnonceSerializer, ReservationSerializer


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from .models import Annonce, Voyage
from .serializers import AnnonceSerializer, VoyageSerializer
from common.utils import reponses, generate_reference


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
                'est_publie': True,
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

    def post(self, request, annonce_id):
        try:
            annonce = Annonce.objects.get(id=annonce_id)

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
                'annonce': annonce_id
            }

            serializer = ReservationSerializer(data=reservation_data)
            if not serializer.is_valid():
                return Response(reponses(success=0, error_msg=serializer.errors))

            reservation = serializer.save()

            # Mettre à jour les kg disponibles
            annonce.nombre_kg_dispo -= int(request.data['nombre_kg'])
            annonce.save()

            # Notifier l'annonceur
            self._notifier_annonceur(annonce, reservation)

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


class ConfirmerReceptionColisAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, reservation_id):
        try:
            reservation = Reservation.objects.select_related('annonce').get(id=reservation_id)

            # Vérifier que c'est bien l'annonceur qui confirme
            if request.user != reservation.annonce.createur:
                return Response(reponses(success=0, error_msg='Non autorisé'))

            # Mettre à jour le statut de la réservation
            reservation.statut = 'REMIS'
            reservation.save()

            # Générer et envoyer le code de confirmation au destinataire
            code_confirmation = generate_reference()
            ctx = {
                'code_confirmation': code_confirmation,
                'reservation_ref': reservation.reference
            }
            message = render_to_string('code_confirmation_colis.html', ctx)
            mail = EmailMessage(
                "Code de confirmation de réception",
                message,
                settings.EMAIL_HOST_USER,
                [reservation.telephone_personne_a_contacter]  # Assurez-vous que c'est un email valide
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)

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
            reservation.statut = 'LIVRE'
            reservation.save()

            # Notifier toutes les parties
            self._notifier_parties(reservation)

            return Response(reponses(success=1, results={'message': 'Livraison confirmée avec succès'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))

    def _notifier_parties(self, reservation):
        # Notifier l'expéditeur
        ctx_expediteur = {
            'reservation_ref': reservation.reference
        }
        message_expediteur = render_to_string('confirmation_livraison_expediteur.html', ctx_expediteur)
        mail_expediteur = EmailMessage(
            "Votre colis a été livré",
            message_expediteur,
            settings.EMAIL_HOST_USER,
            [reservation.user.email]
        )
        mail_expediteur.content_subtype = "html"
        mail_expediteur.send(fail_silently=True)

        # Notifier l'annonceur
        ctx_annonceur = {
            'reservation_ref': reservation.reference
        }
        message_annonceur = render_to_string('confirmation_livraison_annonceur.html', ctx_annonceur)
        mail_annonceur = EmailMessage(
            "Livraison confirmée",
            message_annonceur,
            settings.EMAIL_HOST_USER,
            [reservation.annonce.createur.email]
        )
        mail_annonceur.content_subtype = "html"
        mail_annonceur.send(fail_silently=True)
