from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from annonces.models import Annonce
from annonces.models import Compte, Transaction
from users.utils import reponses, generate_reference, generate_password, notify_user
from .serializers import ReservationSerializer
from django.db import transaction
from annonces.models import Reservation
from django.core.paginator import Paginator




class ReserverKilogrammesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            annonce = Annonce.objects.get(id=request.data['annonce_id'])
            if annonce.user_id.id == request.user.id:
                return Response(reponses(success=0, error_msg='Vous ne pouvez pas faire de réservation sur une annonce que vous avez publié'))

            # Calculer la somme des kg réservés (non annulés ni pending)
            reserved_kg = Reservation.objects.filter(
                annonce=annonce,
                statut__in=['VALIDATE', 'CONFIRM', 'RECEPTION', 'DELIVRATE']
            ).aggregate(total_kg=Sum('nombre_kg'))['total_kg'] or 0

            requested_kg = int(request.data['nombre_kg'])
            available_kg = annonce.nombre_kg_dispo  # Ou nombre_kg si c'est la capacité totale initiale

            if reserved_kg + requested_kg > available_kg:
                return Response(reponses(success=0, error_msg='Kilogrammes demandés excèdent la capacité disponible'))

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
            response_data = {
                **reservation_serializer.data,
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

            # Calculer la somme des kg réservés (exclure la réservation actuelle)
            reserved_kg = Reservation.objects.filter(
                annonce=annonce,
                statut__in=['VALIDATE', 'CONFIRM', 'RECEPTION', 'DELIVRATE']
            ).exclude(id=reservation.id).aggregate(total_kg=Sum('nombre_kg'))['total_kg'] or 0

            requested_kg = int(request.data['nombre_kg'])
            if reserved_kg + requested_kg > annonce.nombre_kg_dispo:
                return Response(reponses(success=0, error_msg='Kilogrammes demandés excèdent la capacité disponible'))

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
            response_data = {
                **reservation_serializer.data,
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
            reserved_kg = Reservation.objects.filter(
                annonce=annonce,
                statut__in=['VALIDATE', 'CONFIRM', 'RECEPTION', 'DELIVRATE']
            ).exclude(id=reservation.id).aggregate(total_kg=Sum('nombre_kg'))['total_kg'] or 0

            if reserved_kg + reservation.nombre_kg > annonce.nombre_kg_dispo:
                reservation.statut = 'CANCEL'
                reservation.save()
                # TODO: Déclencher remboursement (à implémenter)
                return Response(reponses(success=0, error_msg='Plus de kg disponibles, réservation annulée et remboursement initié'))

            reservation.statut = 'VALIDATE'
            reservation.save()
            annonce.nombre_kg_dispo -= reservation.nombre_kg
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

            # Partie mise à jour : Notification
            ### Début de la mise en évidence ###
            ctx = {'annonce_ref': annonce.reference, 'reservation_ref': reservation.reference, 'kg_reserves': reservation.nombre_kg}
            notify_user(
                user=annonce.user_id,
                subject="Nouvelle réservation",
                template_name='nouvelle_reservation.html',
                context=ctx,
                plain_message=f"Une nouvelle réservation ({reservation.reference}) de {reservation.nombre_kg} kg a été faite sur votre annonce {annonce.reference}"
            )
            ### Fin de la mise en évidence ###
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
            annonce = Annonce.objects.get(id=reservation.annonce.pk)

            # Générer le code de réception
            code_reception = generate_password()
            reservation.code_reception = code_reception
            reservation.statut = 'CONFIRM'
            reservation.save()

            # Gestion des transactions
            user_compte = Compte.objects.get(user=request.user)
            reservation_compte = Compte.objects.get(user=reservation.user)
            transaction_debit = Transaction.objects.get(
                compte=reservation_compte, reservation=reservation, transaction_type="DEBIT", transaction_status="PENDING"
            )
            transaction_credit = Transaction.objects.get(
                compte=user_compte, reservation=reservation, transaction_type="CREDIT", transaction_status="PENDING"
            )
            transaction_debit.transaction_status = "SUCCESSFUL"
            transaction_credit.transaction_status = "SUCCESSFUL"
            transaction_debit.save()
            transaction_credit.save()
            user_compte.calculate_balances()
            reservation_compte.calculate_balances()

            # Partie mise à jour : Notification
            ### Début de la mise en évidence ###
            ctx = {'reservation_ref': reservation.reference, 'code_reception': code_reception}
            notify_user(
                user=reservation.user,
                subject="Code de réception",
                template_name='reception_code.html',
                context=ctx,
                plain_message=f"Votre code de réception pour la réservation {reservation.reference} est : {code_reception}"
            )
            ### Fin de la mise en évidence ###

            return Response(reponses(success=1, results={'message': 'Réservation confirmée, code envoyé .'}))
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


            # Gestion conditionnelle selon le statut initial de la réservation
            ctx = {'reservation_ref': reservation.reference}
            if reservation.statut in ['CONFIRM', 'RECEPTION', 'DELIVRATE']:  # Réservation confirmée
                # Ajout des frais
                fees = Decimal('5.00')  # Exemple, à ajuster selon vos besoins
                amount = reservation.montant - fees

                # Notifications au client et à l'annonceur
                notify_user(
                    user=reservation.user,
                    subject="Réservation annulée",
                    template_name='reservation_cancelled.html',
                    context=ctx,
                    plain_message=f"Votre réservation {reservation.reference} a été annulée avec des frais."
                )
                notify_user(
                    user=annonce.user_id,
                    subject="Réservation annulée",
                    template_name='reservation_cancelled_annonceur.html',
                    context=ctx,
                    plain_message=f"La réservation {reservation.reference} sur votre annonce a été annulée."
                )
            else:  # Réservation non confirmée (PENDING ou VALIDATE)
                # Notification uniquement au client
                notify_user(
                    user=reservation.user,
                    subject="Réservation annulée",
                    template_name='reservation_cancelled.html',
                    context=ctx,
                    plain_message=f"Votre réservation {reservation.reference} a été annulée."
                )

            # Annuler la réservation et ajuster les kg disponibles
            reservation.statut = 'CANCEL'
            reservation.save()
            annonce.nombre_kg_dispo += reservation.nombre_kg
            annonce.save()

            return Response(reponses(success=1, results={'message': 'Réservation annulée avec succès'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))




class CancelReservationByReserveurAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.query_params['reservation_id'], user=request.user)
            annonce = Annonce.objects.get(id=reservation.annonce.pk)
            voyage = annonce.voyage

            # Vérifier le délai pour les réservations confirmées
            if reservation.statut in ['CONFIRM', 'RECEPTION', 'DELIVRATE']:
                if voyage.date_depart - timezone.now() < timedelta(days=2):
                    return Response(reponses(success=0, error_msg='Annulation impossible à moins de 2 jours du départ'))

            reservation.statut = 'CANCEL'
            reservation.save()
            annonce.nombre_kg_dispo += reservation.nombre_kg
            annonce.save()

            if reservation.statut in ['VALIDATE', 'CONFIRM', 'RECEPTION', 'DELIVRATE']:
                # Frais pour réservations publiées
                frais = Decimal('5.00')
                Transaction.objects.create(
                    montant=frais,
                    compte=Compte.objects.get(user=request.user),
                    transaction_type="DEBIT",
                    transaction_status="SUCCESSFUL",
                    reservation=reservation
                )
                Compte.objects.get(user=request.user).calculate_balances()

            # Notification
            ctx = {'reservation_ref': reservation.reference}
            message = render_to_string('reservation_cancelled.html', ctx)
            send_email_async("Réservation annulée", message, request.user.email)

            return Response(reponses(success=1, results={'message': 'Réservation annulée'}))
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
                return Response(reponses(success=0, error_msg='Code de réception invalide'))

            code_livraison = generate_password()
            reservation.code_livraison = code_livraison
            reservation.statut = 'RECEPTION'
            reservation.save()

            # Partie mise à jour : Notification
            ### Début de la mise en évidence ###
            ctx = {'reservation_ref': reservation.reference, 'code_livraison': code_livraison}
            notify_user(
                user=reservation.user,
                subject="Code de livraison",
                template_name='livraison_code.html',
                context=ctx,
                plain_message=f"Votre code de livraison pour la réservation {reservation.reference} est : {code_livraison}"
            )
            ### Fin de la mise en évidence ###

            return Response(reponses(success=1, results={'message': 'Colis reçu, code de livraison envoyé'}))
        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))




class LivraisonColisReservationAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        try:
            reservation = Reservation.objects.get(id=request.data['reservation_id'])
            if reservation.code_livraison != request.data['code_livraison']:
                return Response(reponses(success=0, error_msg='Code de livraison invalide'))

            reservation.statut = 'DELIVRATE'
            reservation.save()
            annonce = reservation.annonce
            annonce.active = False
            annonce.save()

            # Mise à jour des transactions
            transaction_credit = Transaction.objects.get(
                compte=Compte.objects.get(user=annonce.user_id),
                reservation=reservation,
                transaction_type="CREDIT"
            )
            transaction_credit.transaction_status = "SUCCESSFUL"
            transaction_credit.save()

            # Partie mise à jour : Notifications
            ### Début de la mise en évidence ###
            ctx = {'reservation_ref': reservation.reference}
            notify_user(
                user=reservation.user,
                subject="Colis livré",
                template_name='colis_delivered.html',
                context=ctx,
                plain_message=f"Votre colis {reservation.reference} a été livré."
            )

            ctx_rating = {'reservation_ref': reservation.reference, 'annonceur_id': annonce.user_id.id}
            notify_user(
                user=reservation.user,
                subject="Évaluez votre expérience",
                template_name='rating_request.html',
                context=ctx_rating,
                plain_message=f"Veuillez évaluer votre expérience pour la réservation {reservation.reference}."
            )
            notify_user(
                user=annonce.user_id,
                subject="Évaluez votre client",
                template_name='rating_request.html',
                context=ctx_rating,
                plain_message=f"Veuillez évaluer le client pour la réservation {reservation.reference}."
            )
            ### Fin de la mise en évidence ###

            # TODO: Planifier virement dans 24h (utiliser Celery ou une tâche différée)
            # Exemple : schedule_transfer(annonce.user_id, reservation.montant, delay=24h)

            return Response(reponses(success=1, results={'message': 'Colis livré, processus terminé'}))
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


