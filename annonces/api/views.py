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
from users.utils import reponses, generate_reference
from .serializers import AnnonceSerializer, VoyageSerializer, TypeBagageSerializer, AnnonceDetailSerializer, \
    AvisUserSerializer
from ..models import Annonce, TypeBagageAnnonce, Voyage
from django.core.paginator import Paginator



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
                'published': False,
                # 'type_bagage_auto': request.data['type_bagage_auto'],
                'nombre_kg_dispo': nombre_kg,
                'montant_par_kg': montant_par_kg,
                'cout_total': cout_total,
                'reference': generate_reference(),
                'voyage': voyage.id,
                'user_id': request.user.id
            }

            annonce_serializer = AnnonceSerializer(data=annonce_data)
            print("############### :", annonce_data)
            if not annonce_serializer.is_valid():
                print("====== :",annonce_serializer.errors)
                return Response(reponses(
                    success=0,
                    error_msg='Données d\'annonce invalides: '+ str(annonce_serializer.errors),
                ))

            annonce = annonce_serializer.save()
            # list_id_bagage_auto = list()
            # for rec in request.data['list_bagage']:
            #     bagage = TypeBagage.objects.get(pk=rec)
            #     list_id_bagage_auto.append(TypeBagageAnnonce(type_bagage=bagage,annonce=annonce))
            #
            # TypeBagageAnnonce.objects.bulk_create(list_id_bagage_auto)
            # # 3. Préparer la réponse avec les données combinées
            # list_bagage_auto = TypeBagage.objects.filter(id__in=request.data['list_bagage'])
            response_data = {
                **annonce_serializer.data,
                # 'voyage': voyage_serializer.data,
                #'bagage_auto': TypeBagageSerializer(list_bagage_auto,many=True).data,
            }

            return Response(reponses(success=1, results=response_data))

        # except Exception as e:
        #     return Response(reponses(success=0, error_msg=str(e)))



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
            # list_id_bagage_auto = list()
            # for rec in request.data['list_bagage']:
            #     bagage = TypeBagage.objects.get(pk=rec)
            #     list_id_bagage_auto.append(TypeBagageAnnonce(type_bagage=bagage,annonce=annonce))
            #
            # TypeBagageAnnonce.objects.bulk_create(list_id_bagage_auto)
            # # 3. Préparer la réponse avec les données combinées
            # list_bagage_auto = TypeBagage.objects.filter(id__in=request.data['list_bagage'])
            response_data = {
                **annonce_serializer.data,
                #'bagage_auto': TypeBagageSerializer(list_bagage_auto,many=True).data,
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
            send_email_async("Livraison du colis", message, reservation.user.email)

            return Response(reponses(success=1, results={'message': 'Livraison confirmée avec succès'}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))


class AnnoncesListAPIView(APIView):
    permission_classes = [AllowAny]

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

        annonces = Annonce.objects.all()
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
            [annonce.user_id.email]
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





from datetime import datetime
from django.db.models import Q, Avg


class AnnonceSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        queryset = Annonce.objects.filter(active=True)

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
        data["utilisateur_auteur"] = request.user.id  # L'utilisateur connecté donne l'avis

        # Validate that either annonce or reservation is provided, not both
        if ('annonce' in data and 'reservation' in data) or ('annonce' not in data and 'reservation' not in data):
            res = reponses(success=0, results={}, error_msg="Un avis doit être lié soit à une réservation, soit à une annonce, mais pas les deux.")
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg="")
            return Response(res, status=status.HTTP_201_CREATED)

        res = reponses(success=0, results={}, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)




class ListerAvisRecusAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvisUserSerializer
    pagination_class = PageNumberPagination  # Optional: Add pagination

    def get_queryset(self):
        """ Filtrage selon des query parameters """
        queryset = AvisUser.objects.filter(utilisateur_note=self.request.user).order_by('-date_creation')

        # Filtre par date
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date_creation__date=date)

        # Filtre par type (annonce ou reservation)
        type_avis = self.request.query_params.get('type', None)
        if type_avis == 'annonce':
            queryset = queryset.filter(annonce__isnull=False)
        elif type_avis == 'reservation':
            queryset = queryset.filter(reservation__isnull=False)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            res = reponses(success=1, results=paginated_data, error_msg="")
            return Response(res)

        serializer = self.get_serializer(queryset, many=True)
        res = reponses(success=1, results=serializer.data, error_msg="")
        return Response(res)



class VoirAvisUtilisateurAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvisUserSerializer
    pagination_class = PageNumberPagination  # Optional: Add pagination

    def get_queryset(self):
        """ Retourne les avis donnés à un utilisateur spécifique """
        utilisateur_id = self.request.query_params.get('utilisateur_id', None)
        if not utilisateur_id:
            return AvisUser.objects.none()

        queryset = AvisUser.objects.filter(utilisateur_note=utilisateur_id).order_by('-date_creation')

        # Filtre par type (annonce ou reservation)
        type_avis = self.request.query_params.get('type', None)
        if type_avis == 'annonce':
            queryset = queryset.filter(annonce__isnull=False)
        elif type_avis == 'reservation':
            queryset = queryset.filter(reservation__isnull=False)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            res = reponses(success=1, results=paginated_data, error_msg="")
            return Response(res)

        serializer = self.get_serializer(queryset, many=True)
        res = reponses(success=1, results=serializer.data, error_msg="")
        return Response(res)







