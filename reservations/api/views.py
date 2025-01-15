from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from .models import Annonce, Reservation
from .serializers import AnnonceSerializer, ReservationSerializer
from common.utils import reponses, generate_reference




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



