from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from annonces.models import Annonce
from users.utils import reponses, generate_reference
from .serializers import ReservationSerializer

from ..models import Reservation


class CreateReserverKilogrammesAPIView(APIView):
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
                'statut': 'PENDING',
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

            # Notifier l'annonceur
            self._notifier_annonceur(annonce, reservation)

            return Response(reponses(success=1, results=serializer.data))

        except Annonce.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



class UpdateReserverKilogrammesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.data['reservation_id'])
            annonce = Annonce.objects.get(id=request.data['annonce_id'])

            if annonce.nombre_kg_dispo < int(request.data['nombre_kg']):
                return Response(reponses(success=0, error_msg='Kilogrammes demandés non disponibles'))

            # Modifier la réservation
            reservation.nombre_kg = request.data['nombre_kg']
            reservation.montant = Decimal(request.data['nombre_kg']) * annonce.montant_par_kg
            reservation.nom_personne_a_contacter = request.data['nom_personne_a_contacter']
            reservation.nombre_kg = request.data['nombre_kg']
            reservation.nombre_kg = request.data['nombre_kg']

            serializer = ReservationSerializer(reservation)
            reservation.save()
            # Mettre à jour les kg disponibles
            annonce.nombre_kg_dispo -= int(request.data['nombre_kg'])
            annonce.save()


            return Response(reponses(success=1, results=serializer.data))

        except Annonce.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))






class CancelReservationAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            annonce = Annonce.objects.get(id=reservation.annonce.pk)
            # Mettre à jour le statut de la réservation
            reservation.statut = 'CANCEL'
            reservation.save()
            annonce.nombre_kg_dispo += int(reservation.nombre_kg)
            annonce.save()
            return Response(reponses(success=1, results={'message': 'Reservation annulée avec succès'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
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



