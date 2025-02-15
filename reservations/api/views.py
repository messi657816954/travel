from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from annonces.models import Annonce, TypeBagageReservation
from annonces.models import Compte, Transaction
from commons.api.serializers import TypeBagageSerializer
from commons.models import TypeBagage
from users.utils import reponses, generate_reference, generate_password
from .serializers import ReservationSerializer
from django.db import transaction
from annonces.models import Reservation
from django.core.paginator import Paginator





class ReserverKilogrammesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            annonce = Annonce.objects.get(id=request.data['annonce_id'])
            if annonce.nombre_kg_dispo < int(request.data['nombre_kg']):
                return Response(reponses(success=0, error_msg='Kilogrammes demandés non disponibles'))

            montant_reservation= Decimal(request.data['nombre_kg']) * annonce.montant_par_kg
            # check si le solde theorique de son compte est superieur au montant de la reservation
            compte = Compte.objects.get(user=request.user)
            balances = compte.calculate_balances()
            # if balances['real_balance'] == 0:
            #     return Response(reponses(success=0, error_msg='Recharger votre compte .'))
            #
            # if montant_reservation < balances['virtual_balance']:
            #     return Response(reponses(success=0, error_msg='Kilogrammes demandés non disponibles'))

            # Créer la réservation pending
            reservation_data = {
                'nombre_kg': request.data['nombre_kg'],
                'montant': Decimal(request.data['nombre_kg']) * annonce.montant_par_kg,
                'nom_personne_a_contacter': request.data['nom_personne_a_contacter'],
                'telephone_personne_a_contacter': request.data['telephone_personne_a_contacter'],
                'description': request.data['description'],
                'statut': 'PENDING',
                'reference': generate_reference(),
                'user': request.user.id,
                'annonce': request.data['annonce_id']
            }

            reservation_serializer = ReservationSerializer(data=reservation_data)
            if not reservation_serializer.is_valid():
                return Response(reponses(success=0, error_msg=reservation_serializer.errors))

            reservation = reservation_serializer.save()

            list_id_bagage_auto = list()
            for rec in request.data['list_bagage']:
                bagage = TypeBagage.objects.get(pk=rec)
                list_id_bagage_auto.append(TypeBagageReservation(type_bagage=bagage,reservation=reservation))

            TypeBagageReservation.objects.bulk_create(list_id_bagage_auto)
            # 3. Préparer la réponse avec les données combinées
            list_bagage_auto = TypeBagage.objects.filter(id__in=request.data['list_bagage'])
            response_data = {
                **reservation_serializer.data,
                # 'voyage': voyage_serializer.data,
                'type_bagage': TypeBagageSerializer(list_bagage_auto,many=True).data,
            }

            return Response(reponses(success=1, results=response_data))

        except Annonce.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



class UpdateReserverKilogrammesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.data['reservation_id'],statut="PENDING")
            annonce = Annonce.objects.get(id=reservation.annonce.id)

            if annonce.nombre_kg_dispo < int(request.data['nombre_kg']):
                return Response(reponses(success=0, error_msg='Kilogrammes demandés non disponibles'))

            montant_reservation = Decimal(request.data['nombre_kg']) * annonce.montant_par_kg
            # check si le solde theorique de son compte est superieur au montant de la reservation
            compte = Compte.objects.get(user=request.user)
            balances = compte.calculate_balances()
            # if balances['real_balance'] == 0:
            #     return Response(reponses(success=0, error_msg='Recharger votre compte .'))
            #
            # if montant_reservation < balances['virtual_balance']:
            #     return Response(reponses(success=0, error_msg='Kilogrammes demandés non disponibles'))

            # Créer la réservation pending
            reservation_data = {
                'nombre_kg': request.data['nombre_kg'],
                'montant': Decimal(request.data['nombre_kg']) * annonce.montant_par_kg,
                'nom_personne_a_contacter': request.data['nom_personne_a_contacter'],
                'telephone_personne_a_contacter': request.data['telephone_personne_a_contacter'],
            }

            reservation_serializer = ReservationSerializer(reservation, data=reservation_data, partial=True)
            if not reservation_serializer.is_valid():
                return Response(reponses(success=0, error_msg=reservation_serializer.errors))

            reservation = reservation_serializer.save()
            TypeBagageReservation.objects.filter(reservation=reservation).delete()
            list_id_bagage_auto = list()
            for rec in request.data['list_bagage']:
                bagage = TypeBagage.objects.get(pk=rec)
                list_id_bagage_auto.append(TypeBagageReservation(type_bagage=bagage,reservation=reservation))

            TypeBagageReservation.objects.bulk_create(list_id_bagage_auto)
            # 3. Préparer la réponse avec les données combinées
            list_bagage_auto = TypeBagage.objects.filter(id__in=request.data['list_bagage'])
            response_data = {
                **reservation_serializer.data,
                'bagage_auto': TypeBagageSerializer(list_bagage_auto,many=True).data,
            }

            return Response(reponses(success=1, results=response_data))

        except Annonce.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class PublishReservationAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.query_params['reservation_id'])
            annonce = Annonce.objects.get(id=reservation.annonce.pk)
            # Mettre à jour le statut de la réservation
            reservation.statut = 'VALIDATE'
            reservation.save()
            annonce.nombre_kg_dispo -= int(reservation.nombre_kg)
            annonce.save()
            user_compte = Compte.objects.get(user=request.user)  # Compte de l'utilisateur connecté
            annonce_compte = Compte.objects.get(user=annonce.user_id)  # Compte de l'utilisateur de l'annonce

            # Créer les transactions
            from decimal import Decimal  # Pour gérer les montants
            montant = Decimal(reservation.montant)

            # Transaction DEBIT pour l'utilisateur connecté
            Transaction.objects.create(
                montant=montant,
                reservation=reservation,
                compte=user_compte,
                transaction_type="DEBIT",
                transaction_status="PENDING",
            )
            # Transaction CREDIT pour l'utilisateur de l'annonce
            Transaction.objects.create(
                montant=montant,
                reservation=reservation,
                compte=annonce_compte,
                transaction_type="CREDIT",
                transaction_status="PENDING",
            )
            user_compte.calculate_balances()
            annonce_compte.calculate_balances()
            return Response(reponses(success=1, results={'message': 'Reservation validée avec succès'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class ConfirmReservationByAnnonceurAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.query_params['reservation_id'])
            # Mettre à jour le statut de la réservation
            code_reception = generate_password()
            print("-----------code_reception-----: ",code_reception)
            reservation.statut = 'VALIDATE'
            reservation.code_reception = code_reception
            reservation.save()
            user_compte = Compte.objects.get(user=request.user)  # Compte de l'utilisateur connecté
            reservation_compte = Compte.objects.get(user=reservation.user)  # Compte de l'utilisateur de l'annonce

            # Confirmer Transaction DEBIT
            transaction_debit = Transaction.objects.get(compte=reservation_compte,reservation=reservation,transaction_status="PENDING",transaction_type="DEBIT")
            transaction_credit = Transaction.objects.get(compte=user_compte,reservation=reservation,transaction_status="PENDING",transaction_type="CREDIT")
            transaction_debit.transaction_status  = "SUCCESSFUL"
            transaction_credit.transaction_status = "SUCCESSFUL"
            transaction_credit.save()
            transaction_debit.save()
            user_compte.calculate_balances()
            reservation_compte.calculate_balances()
            return Response(reponses(success=1, results={'message': 'Reservation annulée avec succès'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class CancelReservationByAnnonceurAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.query_params['reservation_id'])
            annonce = Annonce.objects.get(id=reservation.annonce.pk)
            # Mettre à jour le statut de la réservation
            reservation.statut = 'CANCEL'
            reservation.save()
            annonce.nombre_kg_dispo += int(reservation.nombre_kg)
            annonce.save()
            user_compte = Compte.objects.get(user=request.user)  # Compte de l'utilisateur connecté
            reservation_compte = Compte.objects.get(user=reservation.user)  # Compte de l'utilisateur de l'annonce

            # Confirmer Transaction DEBIT
            transaction_debit = Transaction.objects.get(compte=reservation_compte,reservation=reservation,transaction_status="PENDING")
            transaction_credit = Transaction.objects.get(compte=user_compte,reservation=reservation,transaction_status="PENDING")
            transaction_debit.transaction_status  = "CANCEL"
            transaction_credit.transaction_status = "CANCEL"
            transaction_credit.save()
            transaction_debit.save()
            user_compte.calculate_balances()
            reservation_compte.calculate_balances()
            return Response(reponses(success=1, results={'message': 'Reservation annulée avec succès'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



class CancelReservationByReserveurAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.query_params['reservation_id'])
            # Mettre à jour le statut de la réservation
            reservation.statut = 'CANCEL'
            reservation.save()
            return Response(reponses(success=1, results={'message': 'Reservation annulée avec succès'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class ReceptionColisReservationAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.data['reservation_id'])
            if reservation.code_reception != request.data['code_reception']:
                return Response(reponses(success=0, error_msg='Le code de reception du colis ne correspond pas au code de la reservation'))
            # Mettre à jour le statut de la réservation
            code_livraison = generate_password()
            print("-----------code_livraison-----: ",code_livraison)
            reservation.statut = 'RECEPTION'
            reservation.code_livraison = code_livraison
            reservation.save()

            # todo : envoyer le code livraison par email
            return Response(reponses(success=1, results={'message': 'Reservation annulée avec succès'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class LivraisonColisReservationAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.data['reservation_id'])
            if reservation.code_livraison != request.data['code_livraison']:
                return Response(reponses(success=0, error_msg='Le code de livraison du colis ne correspond pas au code de livraison de la reservation'))
            # Mettre à jour le statut de la réservation
            print("-----------code_livraison-----: ",reservation.code_livraison)
            print("-----------request.data['code_livraison']-----: ",request.data['code_livraison'])
            reservation.statut = 'DELIVRATE'
            reservation.save()

            # todo : envoyer le message de livraison livraison par email
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

    def get_object(self, reservation_id):
        try:
            return Reservation.objects.get(pk=reservation_id, user=self.request.user)
        except Reservation.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        reserve = self.get_object(request.query_params['reservation_id'])
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
            [annonce.user_id.email]
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)



class ReservationsListByAnnonceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if 'page' in request.query_params or 'annonce_id' in request.query_params:
            moyens = Reservation.objects.filter(annonce__pk=request.query_params['annonce_id'])
            paginator = Paginator(moyens, 5)
            page = request.query_params['page']
            moyens = paginator.get_page(page)
            print(moyens)
            serializer = ReservationSerializer(moyens, many=True)
            counts = paginator.num_pages
            print('serializer.data', serializer.data)
            res = reponses(success=1, results=serializer.data,num_page=counts)
            return Response(res)
        return Response(reponses(success=0, error_msg="Spécifiez la page et l'identifiant de l'annonce!"))


