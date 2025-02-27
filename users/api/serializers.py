from commons.models import Pays
from users.models import User, Compte, MoyenPaiementUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from commons.api.serializers import PaysSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        # Validez les données et obtenez les tokens
        data = super().validate(attrs)

        # Ajoutez les informations de l'utilisateur à la réponse
        user = self.user
        cpte = Compte.objects.get(user=user)
        moyens = MoyenPaiementUser.objects.filter(user=user)
        pays = Pays.objects.filter(id=user.pays.id)
        data['user'] = {
            'id': user.id,
            'user_name': user.user_name,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'phone': user.phone,
            'pays': PaysSerializer(pays, many=True).data,
            # Ajoutez d'autres champs de l'utilisateur si nécessaire
        }
        data['compte'] = {
            'id': cpte.id,
            'virtual_balance': cpte.virtual_balance,
            'real_balance': cpte.real_balance,
            # Ajoutez d'autres champs de l'utilisateur si nécessaire
        }
        data['infos_methode_paiement'] = MoyenPaiementSerializer(moyens, many=True).data

        return data

    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)
    #     return token

class RegistrationSerializer(serializers.ModelSerializer):
    # password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    pays_details = PaysSerializer(source='pays', read_only=True)
    class Meta:
        model = User
        fields =  ['email','firstname','lastname', 'user_name','phone', 'password', 'otp', 'pays_details', 'pays']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def save(self):
        pays = self.validated_data['pays']
        user = User(email=self.validated_data['email'],firstname=self.validated_data['firstname'],lastname=self.validated_data['lastname'],
                    user_name=self.validated_data['user_name'],is_active=True,phone=self.validated_data['phone'])
        user.set_password(self.validated_data['password'],)
        user.pays=pays
        user.save()
        return user
                    
class VerifyOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()
    otp = serializers.CharField()




class CompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compte
        fields = '__all__'



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'firstname', 'lastname', 'user_name', 'phone','is_phone_verify','pays']



class MoyenPaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoyenPaiementUser
        fields = '__all__'







# class CustomTokenRefreshViewSerializer(TokenRefreshView):
#     def validate(self, attrs):
#         # The default result (access/refresh tokens)
#         data = super(CustomTokenRefreshViewSerializer, self).validate(attrs)
#         # Custom data you want to include
#         data.update({'user': self.user.username})
#         data.update({'id': self.user.id})
#         # and everything else you want to send in the response
#         return data

# class LoginTokenGenerationSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField()
    
