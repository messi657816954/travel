from django.utils import timezone
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import *
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal

from commons.models import TypeBagage, Pays, Ville
from annonces.models import Reservation, AvisUser
from users.models import User
from users.utils import reponses, generate_reference
from .serializers import AnnonceSerializer, VoyageSerializer, TypeBagageSerializer, AnnonceDetailSerializer, \
    AvisUserSerializer, AvisRecusSerializer, AvisDonnesSerializer
from ..models import Annonce, TypeBagageAnnonce, Voyage
from django.core.paginator import Paginator
from reservations.api.views import cancelReservation



class CreateAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        if not request.user.is_phone_verify or not request.user.is_identity_check:
            return Response(reponses(
                success=0,
                error_msg='This action is only available to users who have verified their phone number and identity.'
            ))

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
        nombre_kg_dispo = Decimal(request.data['nombre_kg_dispo'])
        cout_total = montant_par_kg * nombre_kg

        annonce_data = {
            'published': False,
            'nombre_kg_dispo': nombre_kg_dispo,
            'nombre_kg': nombre_kg,
            'montant_par_kg': montant_par_kg,
            'cout_total': cout_total,
            'reference': generate_reference(),
            'voyage': voyage.id,
            'user_id': request.user.id
        }

        annonce_serializer = AnnonceSerializer(data=annonce_data)
        if not annonce_serializer.is_valid():
            return Response(reponses(
                success=0,
                error_msg='Données d\'annonce invalides: '+ str(annonce_serializer.errors),
            ))

        annonce = annonce_serializer.save()
        response_data = {
            **annonce_serializer.data,
            'voyage': voyage_serializer.data,
        }

        return Response(reponses(success=1, results=response_data))



class UpdateAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            # 1. Créer d'abord le voyage annonce.published = True
            #             annonce.active = True
            annonce = Annonce.objects.get(id=request.data['annonce_id'])
            if annonce.published == True or annonce.active == False:
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
                'nombre_kg': nombre_kg,
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

            response_data = {
                **annonce_serializer.data,
            }

            return Response(reponses(success=1, results=response_data))

        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



class PublierAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            annonce = Annonce.objects.get(id=request.query_params['annonce_id'])
            # Mettre à jour le statut de l'annonce'
            annonce.published = True
            annonce.active = True
            annonce.date_publication = timezone.now()
            annonce.save()
            return Response(reponses(success=1, results={'message': 'annonce publiée avec succès.'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Annonce non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))

class CancelAnnonceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        try:
            annonce = Annonce.objects.get(id=request.query_params['annonce_id'])
            reservations = Reservation.objects.filter(annonce__pk=request.query_params['annonce_id'])
            for reservation in reservations:
                cancel = cancelReservation(request, reservation)
                if cancel[0] == 0:
                    return Response(reponses(success=0, error_msg=cancel[1]))

            annonce.published = False
            annonce.canceled = True
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
            annonce.active = False
            annonce.save()
            # TODO: apres le paiement il faut mettre à jour le compte de l'annonceur et faire la transaction

            # Notifier toutes les parties
            ctx = {
                'reservation_ref': reservation.reference
            }
            message = render_to_string('confirm_livraison_colis.html', ctx)
            send_email_async("Livraison du colis", message, [reservation.user.email])

            return Response(reponses(success=1, results={'message': 'Livraison confirmée avec succès'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class AnnoncesListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        annonces = Annonce.objects.filter(user_id=request.user)
        if 'page' in request.query_params:
            pass
            paginator = Paginator(annonces, 5)
            page = request.query_params['page']
            annonces = paginator.get_page(page)
            print(annonces)
            serializer = AnnonceDetailSerializer(annonces, many=True)
            counts = paginator.num_pages

            print('serializer.data', serializer.data)
            res = reponses(success=1, results=serializer.data,num_page=counts)
            return Response(res)
        annonces = Annonce.objects.filter(user_id=request.user)
        serializer = AnnonceDetailSerializer(annonces, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res)



class AllAnnoncesListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        annonces = Annonce.objects.filter(published=True).order_by("-date_publication")
        if 'page' in request.query_params:
            paginator = Paginator(annonces, 5)
            page = request.query_params['page']
            annonces = paginator.get_page(page)
            print(annonces)
            serializer = AnnonceDetailSerializer(annonces, many=True)
            counts = paginator.num_pages
            print('serializer.data', serializer.data)
            res = reponses(success=1, results=serializer.data,num_page=counts)
            return Response(res)
        serializer = AnnonceDetailSerializer(annonces, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res)






class AnnonceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, annonce_id):
        try:
            return Annonce.objects.get(pk=annonce_id, user_id=self.request.user)
        except Annonce.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        annonce = self.get_object(request.query_params['annonce_id'])
        if not annonce:
            res = reponses(success=0, error_msg="Reservation introuvable.")
            return Response(res)
        serializer = AnnonceDetailSerializer(annonce)
        # 3. Préparer la réponse avec les données combinées

        response_data = {
            **serializer.data,
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
            [annonce.user_id.email]
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)



async def send_email_async(subject, message, recipient_email):
    mail = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_email,
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)





from datetime import datetime
from django.db.models import Q, Avg, Count


class AnnonceSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        queryset = Annonce.objects.filter(published=True).order_by("-date_publication")

        # 🔹 Filtrage par date de départ (optionnel)
        date_depart = request.query_params.get('date_depart', None)
        if date_depart:
            try:
                date_obj = datetime.strptime(date_depart, "%Y-%m-%d")
                queryset = queryset.filter(voyage__date_depart__date=date_obj)
            except ValueError:
                return Response({"error": "Format de date invalide. Utilise YYYY-MM-DD"}, status=400)

        # 🔹 Recherche par autocomplétion sur provenance ET destination
        provenance = request.query_params.get('provenance', None)
        destination = request.query_params.get('destination', None)

        villes_prov_dest = []

        if provenance and destination:
            villes_prov_dest = list(Ville.objects.filter(
                Q(intitule__icontains=provenance) | Q(intitule__icontains=destination)
            ).order_by('-id')[:5])

        # 🔹 Récupération des pays liés aux villes trouvées
        pays_prov_dest = list(Pays.objects.filter(villes__in=villes_prov_dest).distinct())

        # 🔹 Ajout des annonces liées aux villes ET aux pays trouvés
        if provenance and destination:
            queryset = queryset.filter(
                Q(voyage__provenance__in=villes_prov_dest) &
                Q(voyage__destination__in=villes_prov_dest) &
                Q(voyage__provenance__pays__in=pays_prov_dest) &
                Q(voyage__destination__pays__in=pays_prov_dest)
            ).distinct()


        # 🔹 Filtrage par poids (min_kg ET max_kg doivent être respectés)
        min_kg = request.query_params.get('min_kg', None)
        max_kg = request.query_params.get('max_kg', None)

        if min_kg and max_kg:
            queryset = queryset.filter(nombre_kg_dispo__gte=int(min_kg), nombre_kg_dispo__lte=int(max_kg))

        # 🔹 Pagination (5 annonces par page)
        page = request.query_params.get('page', 1)
        paginator = Paginator(queryset, 5)
        annonces_page = paginator.get_page(page)

        serializer = AnnonceDetailSerializer(annonces_page, many=True)
        return Response({
            "success": 1,
            "results": serializer.data,
            "num_page": paginator.num_pages
        })



class DonnerAvisAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvisUserSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        query_data = request.query_params.copy()
        utilisateur_note = query_data.get("utilisateur_note",None)
        data["utilisateur_auteur"] = request.user.id  # L'utilisateur connecté donne l'avis


        # Validate that either annonce or reservation is provided, not both
        if ('annonce' in query_data and 'reservation' in query_data) or ('annonce' not in query_data and 'reservation' not in query_data):
            res = reponses(success=0, results={}, error_msg="Un avis doit être lié soit à une réservation, soit à une annonce, mais pas les deux.")
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        if not utilisateur_note :
            res = reponses(success=0, results={}, error_msg="Spécifiez l'utilisateur à noter.")
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


        print(f"Utilisateur authentifié: {request.user.id}")
        data["annonce"] = query_data.get("annonce",None)
        data["reservation"] = query_data.get("reservation",None)
        data["utilisateur_note"] = utilisateur_note

        serializer = self.get_serializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg="")
            return Response(res, status=status.HTTP_201_CREATED)

        res = reponses(success=0, results={}, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)




class UtilisateurAvisView(APIView):
    permission_classes = [AllowAny]  # Autoriser l'accès sans authentification

    def get(self, request):
        try:
            # Récupérer le utilisateur_id depuis les query parameters (noter le nom du paramètre)
            utilisateur_id = request.query_params.get('uuid', None)

            if utilisateur_id is None:
                return Response(
                    [{
                        "success": 0,
                        "errors": [{"error_msg": "utilisateur_id est requis"}]
                    }],
                    status=status.HTTP_200_OK  # Gardons 200 comme dans votre exemple
                )

            try:
                user = User.objects.get(id=utilisateur_id)
            except (User.DoesNotExist, ValueError):
                return Response(
                    [{
                        "success": 0,
                        "errors": [{"error_msg": "Utilisateur non trouvé"}]
                    }],
                    status=status.HTTP_200_OK  # Gardons 200 comme dans votre exemple
                )

            # Récupérer tous les avis reçus par l'utilisateur
            avis_recus = AvisUser.objects.filter(utilisateur_note=user).order_by('-date_creation')

            # Calculer la moyenne des notes
            average = avis_recus.aggregate(Avg('note'))['note__avg'] or 0

            # Compter le nombre total d'avis reçus
            total_avis = avis_recus.count()

            # Calculer la distribution des notes
            note_counts = avis_recus.values('note').annotate(count=Count('note'))
            note_map = {
                '5': 0,
                '4': 0,
                '3': 0,
                '2': 0,
                '1': 0
            }
            for item in note_counts:
                note_map[str(item['note'])] = item['count']

            # Récupérer les avis donnés par l'utilisateur
            avis_donnes = AvisUser.objects.filter(utilisateur_auteur=user).order_by('-date_creation')

            # Sérialiser les données
            avis_recus_serializer = AvisRecusSerializer(avis_recus, many=True)
            avis_donnes_serializer = AvisDonnesSerializer(avis_donnes, many=True)

            # Construire la réponse
            avis_data = {
                'average': round(average, 1),
                'total_avis_recieve': total_avis,
                'map_note_type': note_map,
                'avis_recieve': avis_recus_serializer.data,
                'avis_give': avis_donnes_serializer.data
            }

            # Formater selon votre structure de réponse
            response_data = [{
                "success": 1,
                "data": avis_data
            }]

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Capturer toute exception et la formater selon votre structure de réponse
            return Response(
                [{
                    "success": 0,
                    "errors": [{"error_msg": str(e)}]
                }],
                status=status.HTTP_200_OK  # Gardons 200 comme dans votre exemple
            )









