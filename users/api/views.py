from annonces.models import Reservation
from .serializers import RegistrationSerializer, VerifyOTPSerializer, MyTokenObtainPairSerializer, \
    ChangePasswordSerializer, UserDetailSerializer, CompteSerializer, MoyenPaiementSerializer
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.permissions import *
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from annonces.models import  Paiement, Transaction
from users.models import User, Compte, MoyenPaiementUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404


from django.core.mail import send_mail, EmailMessage
from users.utils import *
from django.conf import settings

from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response

from django.db import transaction




class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            res = reponses(success=0, error_msg=str(e))
            return Response(res)

        # Récupérez la réponse standard
        response_data = serializer.validated_data

        # Personnalisez la réponse selon vos besoins
        custom_response_data = {
            'access_token': response_data.get('access'),
            'refresh_token': response_data.get('refresh'),
            'user': response_data.get('user'),  # Ajoutez les infos de l'utilisateur
            'compte': response_data.get('compte'),  # Ajoutez les infos de l'utilisateur
            'infos_methode_paiement': response_data.get('infos_methode_paiement'),  # Ajoutez les infos de l'utilisateur

        }
        res = reponses(success=1, results=custom_response_data, error_msg='')
        return Response(res)



class RegistrationAPIView(generics.GenericAPIView):
    '''Registers user'''
    serializer_class = RegistrationSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = {}
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # send_otp(serializer.data['email'])
            cpte = Compte.objects.create(
                virtual_balance=0,
                real_balance=0,
                user=user  # Utilisation de l'instance utilisateur
            )
            moyens = MoyenPaiementUser.objects.filter(user=user)
            payment_method = MoyenPaiementSerializer(moyens, many=True)
            compte_serializer = CompteSerializer(cpte)
            data['response'] = "Registration Successful!"
            refresh = RefreshToken.for_user(user=user)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            data['account'] = compte_serializer.data
            data['user'] = self.get_serializer(user).data
            data['user_payment_method'] = payment_method.data

        res = reponses(success=1, results=data, error_msg='')
        return Response(res)



class VerifyOTPAPIView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data['email']
            otp = serializer.data['otp']
            user_obj = User.objects.get(email=email)
            
            if user_obj.otp == otp:
                user_obj.is_staff = True
                user_obj.save()
                res = reponses(success=0, error_msg='verified')
                return Response(res)
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res)



class LogoutBlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            res = reponses(success=1, results="Ok", error_msg='')
            return Response(res)
        except Exception as e:
            res = reponses(success=0,  error_msg='Exception')
            return Response(res)



class InitRegistrationAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        code = generate_password()
        print("------------code",code)
        try:
            User.objects.get(email=request.data['email'])
            msg = 'Un utilisateur avec email {} existe déjà!'.format(request.data['email'])
            res = reponses(success=0, error_msg=msg.encode('utf8'))
            return Response(res)
        except User.DoesNotExist:
            data_response = {
                'email': request.data['email'],
                'code': code
            }
            ctx = {
                'code': code,
                'client': request.data['email']
            }
            message = render_to_string('mail.html', ctx)
            mail = EmailMessage(
                "Création de votre compte LEDJANGUI",
                message,
                settings.EMAIL_HOST_USER,
                [request.data['email']]
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)

            res = reponses(success=1, results=data_response, error_msg='')
            return Response(res)



class PerformRegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        print("--------1----data : ",request.data)
        data_query = {
            'email': request.data['email'],
            'user_name': request.data['user_name'],
            # 'otp': request.data['otp'],
            'password': request.data['password']
        }
        serializer = RegistrationSerializer(data=data_query)
        if serializer.is_valid(raise_exception=True):
            print("-------2-----data : ",request.data)
            user = serializer.save()
            cpte = Compte.objects.create(
                virtual_balance=0,
                real_balance=0,
                incoming_amount=0,
                user=user  # Utilisation de l'instance utilisateur
            )
            compte_serializer = CompteSerializer(cpte)

            # Préparation des données de réponse
            refresh = RefreshToken.for_user(user=user)
            response_data = {
                **serializer.data,  # Données de l'utilisateur
                'access': str(refresh.access_token),  # Données du compte
                'refresh': str(refresh),  # Données du compte
                # 'compte': compte_serializer.data  # Données du compte
            }
            res = reponses(success=1, results=data_query, error_msg='')
            return Response(res)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res)



class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        print("le user is", request.user.user_name)
        logger(request, 'Deconnexion de {} sur le webservice : '.format(request.user.user_name))
        return self.logout(request)


    def logout(self, request,format=None):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            res = reponses(success=0, error_msg='Une erreur est survenue pendant la suppression du token')
            return Response(res)
        logout(request)
        res = reponses(success=1, results="Déconnexion effectué avec Succès".encode('utf8'),error_msg='')
        return Response(res)

# -----------------------------------------------Fin mise àjour des informations des utilisateurs


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]



    def post(self, request, *args, **kwargs):
        self.object = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.data.get("new_password")
            if not self.object.check_password(serializer.data.get("old_password")):
                res = reponses(success=0, results=[],error_msg='Mauvais password! Entrer le bon mot de passe')
                return Response(res)

            self.object.set_password(password)
            self.object.change_password = True
            self.object.save()
            res = reponses(success=1, results="Password a été changé avec succès".encode('utf8'),error_msg='')
            return Response(res)
        res = reponses(success=1, error_msg=serializer.errors)
        return Response(res)



class PerformForgotPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    model = User
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.data['email'])
        if user:
            if user[0].reset_password_code == request.data['code']:
                password = request.data.get("password")
                user[0].set_password(password)
                user[0].save()
                res = reponses(success=1, results="Password a été changé avec succès".encode('utf8'),error_msg='')
                return Response(res)
            res = reponses(success=0, error_msg="Le code ne correspond pas")
            return Response(res)
        res = reponses(success=0, error_msg="Pas d'utilisateur correspondant à cet email")
        return Response(res)




class InitForgotPasswordAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        code = generate_password()
        print("------------code : ",code)
        user = User.objects.filter(email=request.data['email'])
        if user:
            user[0].reset_password_code = code
            user[0].save()

            ctx = {
                'code': code,
                'client': user[0].user_name
            }
            message = render_to_string('mail_forget.html', ctx)
            mail = EmailMessage(
                "Mot de passe oublié",
                message,
                settings.EMAIL_HOST_USER,
                [request.data['email']]
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)

            res = reponses(success=1, results="Code envoyé par email avec succès", error_msg='')
            return Response(res)

        else:
            msg = "Pas d'utilisateur avec cet email {} !".format(request.data['email'])
            res = reponses(success=0, error_msg=msg.encode('utf8'))
            return Response(res)



class UserDetailClientView(APIView):
    permission_classes = [IsAuthenticated ]
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            user_obj = request.user
            data_serializer = self.serializer_class(user_obj)
            cpte = Compte.objects.get(user=request.user)
            compte_serializer = CompteSerializer(cpte)
            moyens = MoyenPaiementUser.objects.filter(user=request.user)
            type_paiement_serializer = MoyenPaiementSerializer(moyens, many=True)
            response_data = {
                **data_serializer.data,  # Données de l'utilisateur
                'compte': compte_serializer.data,  # Données du compte
                'type_paiement': type_paiement_serializer.data  # Données du compte
            }
            res = reponses(success=1, results=response_data)
            return Response(res)
        except User.DoesNotExist:
            res = reponses(success=0, error_msg="Cet utilisateur n'est pas un UTILISATEUR")
            return Response(res)

    def get_object(self):
        user_obj = get_object_or_404(User, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, user_obj)
        return user_obj



class MoyenPaiementListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        moyens = MoyenPaiementUser.objects.filter(user=request.user)
        serializer = MoyenPaiementSerializer(moyens, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = MoyenPaiementSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_201_CREATED)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)



class MoyenPaiementDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return MoyenPaiementUser.objects.get(pk=pk, user=self.request.user)
        except MoyenPaiementUser.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        moyen = self.get_object(pk)
        if not moyen:
            res = reponses(success=0, error_msg="Moyen de paiement introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = MoyenPaiementSerializer(moyen)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        moyen = self.get_object(pk)
        if not moyen:
            res = reponses(success=0, error_msg="Moyen de paiement introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = MoyenPaiementSerializer(moyen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_200_OK)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        moyen = self.get_object(pk)
        if not moyen:
            res = reponses(success=0, error_msg="Moyen de paiement introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        moyen.delete()
        res = reponses(success=1, results="Moyen de paiement supprimé avec succès.", error_msg='')
        return Response(res, status=status.HTTP_204_NO_CONTENT)






























    def reponses(self, success, num_page=None, results=None, error_msg=None):
        RESPONSE_MSG = [{'success': success}]

        if num_page:
            RESPONSE_MSG[0].update({'nombre_page': num_page})
        if results:
            if isinstance(results, list):
                RESPONSE_MSG[0].update({'results': results})
            else:
                RESPONSE_MSG[0].update({'results': [results]})
        if error_msg:
            RESPONSE_MSG[0].update({'errors': [{'error_msg': error_msg}]})

        return RESPONSE_MSG



class InitierPaiementAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            # Créer un nouvel objet Paiement avec l'état 'PENDING'
            paiement = Paiement.objects.create(
                status='PENDING',
                telephone=request.data.get('telephone'),
                numero_carte=request.data.get('numero_carte'),
                email=request.data.get('email'),
                cvv=request.data.get('cvv'),
                date_expiration=request.data.get('date_expiration'),
                user=request.user,
                montant=request.data.get('montant'),
                type=request.data.get('type_paiement'),
                # reservation=reservation
            )
            user_compte = Compte.objects.get(user=request.user)  # Compte de l'utilisateur de l'annonce

            # Créer les transactions
            from decimal import Decimal  # Pour gérer les montants
            montant = Decimal(request.data.get('montant'))

            # Transaction DEBIT pour l'utilisateur connecté
            Transaction.objects.create(
                montant=montant,
                # reservation=reservation,
                compte=user_compte,
                transaction_type="DEPOSITE",
                # transaction_status="PENDING",
                transaction_status="SUCCESSFUL", # pour les tests
                 # pour les tests
            )
            user_compte.calculate_balances() # pour les tests

            # TODO: Ajouter un envoi de notification ou d'email si nécessaire

            return Response(reponses(success=1, results={'message': 'Paiement initié avec succès', 'paiement_id': paiement.id}))

        except Reservation.DoesNotExist:
            return Response(reponses(success=0, error_msg='Réservation non trouvée'))
        except Exception as e:
            return Response(reponses(success=0, error_msg=str(e)))



class InitPhoneOtpAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
# request.data['phone']
        code = generate_password()
        print("------------code otp : ",code)
        user = User.objects.filter(pk=request.user.id)
        if user:
            user[0].otp = code
            user[0].save()
            # todo: envoyer code par sms request.data['phone']

            res = reponses(success=1, results="Code envoyé par sms avec succès", error_msg='')
            return Response(res)

        else:
            msg = "Pas d'utilisateur avec cet email {} !".format(request.data['email'])
            res = reponses(success=0, error_msg=msg.encode('utf8'))
            return Response(res)



class PerformOtpAPIView(APIView):
    model = User
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(pk=request.user.id)
        if user:
            if user[0].otp == request.data['otp']:
                user[0].is_phone_verify = True
                user[0].save()
                res = reponses(success=1, results="Otp a été effectué avec succès".encode('utf8'),error_msg='')
                return Response(res)
            res = reponses(success=0, error_msg="Le code ne correspond pas")
            return Response(res)
        res = reponses(success=0, error_msg="Pas d'utilisateur correspondant à cet email")
        return Response(res)






