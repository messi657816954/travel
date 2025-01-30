from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from commons.models import TypeBagage
from annonces.models import Reservation
from users.utils import reponses, generate_reference
from .serializers import AnnonceSerializer, VoyageSerializer, TypeBagageSerializer, AnnonceDetailSerializer
from ..models import Annonce, TypeBagageAnnonce, Voyage





class CreateAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # try:
            # 1. Créer d'abord le voyage
            voyage_data = {
                'date_depart': request.data['date_depart'],
                'provenance': request.data['provenance'],
                'destination': request.data['destination'],
                'agence_voyage': request.data.get('agence_voyage', ''),
                'code_reservation': request.data.get('code_reservation', ''),
                'moyen_transport': request.data.get('moyen_transport', '')
            }

            voyage_serializer = VoyageSerializer(data=voyage_data)
            if not voyage_serializer.is_valid():
                return Response(reponses(
                    success=0,
                    error_msg='Données de voyage invalides: ' + str(voyage_serializer.errors)
                ))

            voyage = voyage_serializer.save()

            # 2. Créer ensuite l'annonce
            montant_par_kg = Decimal(request.data['montant_par_kg'])
            nombre_kg = Decimal(request.data['nombre_kg_dispo'])
            cout_total = montant_par_kg * nombre_kg

            annonce_data = {
                'est_publie': False,
                # 'type_bagage_auto': request.data['type_bagage_auto'],
                'nombre_kg_dispo': nombre_kg,
                'montant_par_kg': montant_par_kg,
                'cout_total': cout_total,
                'reference': generate_reference(),
                'voyage': voyage.id,
                'createur': request.user.id
            }

            annonce_serializer = AnnonceSerializer(data=annonce_data)
            if not annonce_serializer.is_valid():
                print("====== :",annonce_serializer.errors)
                return Response(reponses(
                    success=0,
                    error_msg='Données d\'annonce invalides: '+ str(annonce_serializer.errors),
                ))

            annonce = annonce_serializer.save()
            list_id_bagage_auto = list()
            for rec in request.data['list_bagage']:
                bagage = TypeBagage.objects.get(pk=rec)
                list_id_bagage_auto.append(TypeBagageAnnonce(type_bagage=bagage,annonce=annonce))

            TypeBagageAnnonce.objects.bulk_create(list_id_bagage_auto)
            # 3. Préparer la réponse avec les données combinées
            list_bagage_auto = TypeBagage.objects.filter(id__in=request.data['list_bagage'])
            response_data = {
                **annonce_serializer.data,
                # 'voyage': voyage_serializer.data,
                'bagage_auto': TypeBagageSerializer(list_bagage_auto,many=True).data,
            }

            return Response(reponses(success=1, results=response_data))

        # except Exception as e:
        #     return Response(reponses(success=0, error_msg=str(e)))



class UpdateAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            # 1. Créer d'abord le voyage annonce.est_publie = True
            #             annonce.est_actif = True
            annonce = Annonce.objects.get(id=request.data['annonce_id'])
            if annonce.est_publie == True or annonce.est_actif == False:
                return Response(reponses(
                    success=0,
                    error_msg='Annonce dejà publiée ou actif',
                ))
            voyage_data = {
                'date_depart': request.data['date_depart'],
                'provenance': request.data['provenance'],
                'destination': request.data['destination'],
                'agence_voyage': request.data.get('agence_voyage', ''),
                'code_reservation': request.data.get('code_reservation', ''),
                'moyen_transport': request.data.get('moyen_transport', '')
            }
            voyage = Voyage.objects.get(id=annonce.voyage.id)
            voyage_serializer = VoyageSerializer(voyage, data=voyage_data, partial=True)
            if not voyage_serializer.is_valid():
                return Response(reponses(
                    success=0,
                    error_msg='Données de voyage invalides:'+ str(voyage_serializer.errors),
                ))

            voyage_serializer.save()

            # 2. Créer ensuite l'annonce
            montant_par_kg = Decimal(request.data['montant_par_kg'])
            nombre_kg = Decimal(request.data['nombre_kg_dispo'])
            cout_total = montant_par_kg * nombre_kg
            annonce_data = {
                # 'type_bagage_auto': request.data['type_bagage_auto'],
                'nombre_kg_dispo': nombre_kg,
                'montant_par_kg': montant_par_kg,
                'cout_total': cout_total,
            }
            annonce_serializer = AnnonceSerializer(annonce, data=annonce_data, partial=True)
            if not annonce_serializer.is_valid():
                return Response(reponses(
                    success=0,
                    error_msg='Données d\'annonce invalides : '+ str(annonce_serializer.errors),
                ))

            annonce = annonce_serializer.save()
            TypeBagageAnnonce.objects.filter(annonce=annonce).delete()
            list_id_bagage_auto = list()
            for rec in request.data['list_bagage']:
                bagage = TypeBagage.objects.get(pk=rec)
                list_id_bagage_auto.append(TypeBagageAnnonce(type_bagage=bagage,annonce=annonce))

            TypeBagageAnnonce.objects.bulk_create(list_id_bagage_auto)
            # 3. Préparer la réponse avec les données combinées
            list_bagage_auto = TypeBagage.objects.filter(id__in=request.data['list_bagage'])
            response_data = {
                **annonce_serializer.data,
                'bagage_auto': TypeBagageSerializer(list_bagage_auto,many=True).data,
            }

            return Response(reponses(success=1, results=response_data))

        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



class PublierAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, annonce_id):
        try:
            annonce = Annonce.objects.get(id=annonce_id)
            # Mettre à jour le statut de l'annonce'
            annonce.est_publie = True
            annonce.est_actif = True
            annonce.date_publication = timezone.now()
            annonce.save()
            return Response(reponses(success=1, results={'message': 'annonce publiée avec succès.'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class ConfirmerLivraisonAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            code_confirmation = request.data.get('code_confirmation')
            reservation_id = request.data.get('reservation_id')
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
            send_email_async("Livraison du colis", message, reservation.user.email)

            return Response(reponses(success=1, results={'message': 'Livraison confirmée avec succès'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class AnnoncesListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        annonces = Annonce.objects.filter(createur=request.user)
        serializer = AnnonceDetailSerializer(annonces, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res)



class AnnonceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Annonce.objects.get(pk=pk, createur=self.request.user)
        except Annonce.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        annonce = self.get_object(pk)
        if not annonce:
            res = reponses(success=0, error_msg="Reservation introuvable.")
            return Response(res)
        serializer = AnnonceDetailSerializer(annonce)
        # 3. Préparer la réponse avec les données combinées
        # list_bagage_auto = TypeBagage.objects.filter(id__in=request.data['list_bagage'])
        list_bagage_auto = TypeBagage.objects.filter(
                                type_bagage_annonces__annonce=annonce
                            ).distinct()

        response_data = {
            **serializer.data,
            'bagage_auto': TypeBagageSerializer(list_bagage_auto,many=True).data,
        }
        res = reponses(success=1, results=response_data, error_msg='')
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



async def send_email_async(subject, message, recipient_email):
    mail = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [recipient_email],
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)
