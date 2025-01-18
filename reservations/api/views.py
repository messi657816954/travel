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
                'nom_personne_a_contacter': request.data['nom_personne_a_contacter'],
                'telephone_personne_a_contacter': request.data['telephone_personne_a_contacter'],
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
            # self._notifier_annonceur(annonce, reservation)

            return Response(reponses(success=1, results=serializer.data))

        except Annonce.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



class UpdateReserverKilogrammesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request,annonce_id):
        try:
            reservation = Reservation.objects.get(id=request.data['reservation_id'])
            annonce = Annonce.objects.get(id=annonce_id)

            if annonce.nombre_kg_dispo < int(request.data['nombre_kg']):
                return Response(reponses(success=0, error_msg='Kilogrammes demandés non disponibles'))

            data = request.data.copy()
            data['montant'] = Decimal(request.data['nombre_kg']) * annonce.montant_par_kg
            serializer = ReservationSerializer(reservation, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # Mettre à jour les kg disponibles
                annonce.nombre_kg_dispo -= int(request.data['nombre_kg'])
                annonce.save()
                return Response(reponses(success=1, results=serializer.data))
            res = reponses(success=0, error_msg=serializer.errors)
            return Response(res)

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



class ReservationsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        moyens = Reservation.objects.filter(user=request.user)
        serializer = ReservationSerializer(moyens, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res)

class ReservationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Reservation.objects.get(pk=pk, user=self.request.user)
        except Reservation.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        reserve = self.get_object(pk)
        if not reserve:
            res = reponses(success=0, error_msg="Reservation introuvable.")
            return Response(res)
        serializer = ReservationSerializer(reserve)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res)



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



