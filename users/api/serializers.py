from django.contrib.auth import authenticate

from commons.models import Pays
from users.models import User, Compte, MoyenPaiementUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from commons.api.serializers import PaysSerializer
from django.contrib.auth.password_validation import validate_password


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add phone to the default fields
        self.fields['phone'] = serializers.CharField(required=False)
        # Make email optional since we'll allow phone login
        self.fields['email'].required = False

    def validate(self, attrs):
        # Get credentials
        from transactions.api.views import get_user_balance_info
        email = attrs.get('email')
        phone = attrs.get('phone')
        password = attrs.get('password')

        if not email and not phone:
            raise serializers.ValidationError(
                'Must include either "email" or "phone" with password.'
            )

        # Authenticate with either email or phone
        user = None
        if email:
            user = authenticate(request=self.context['request'],
                              email=email, password=password)
        elif phone:
            try:
                user_obj = User.objects.get(phone=phone)
                user = authenticate(request=self.context['request'],
                                  email=user_obj.email, password=password)
            except User.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError(
                'No active account found with the given credentials'
            )

        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': RegistrationSerializer(user).data,
            'balance': get_user_balance_info(user.id)
        }

        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class RegistrationSerializer(serializers.ModelSerializer):
    # password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    pays_details = PaysSerializer(source='pays', read_only=True)
    class Meta:
        model = User
        fields =  ['email','firstname','lastname', 'user_name','phone', 'password', 'pays_details', 'is_phone_verify', 'is_identity_check', 'address', 'city', 'zip_code', 'pays', 'profile_picture']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def save(self):
        pays = self.validated_data['pays']
        user = User(email=self.validated_data['email'],
                    firstname=self.validated_data['firstname'],
                    lastname=self.validated_data['lastname'],
                    user_name=self.validated_data['user_name'],
                    is_active=True,
                    phone=self.validated_data['phone']
                    )
        user.set_password(self.validated_data['password'],)
        user.pays=pays
        user.save()
        return user

class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['lastname', 'firstname', 'address', 'city', 'zip_code']

    def update(self, instance, validated_data):
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.save()
        return instance
                    
class VerifyOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()
    otp = serializers.CharField()




class CompteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compte
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(use_url=True)
    pays_details = PaysSerializer(source='pays', read_only=True)

    moyenne_notes = serializers.SerializerMethodField()
    avis_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'firstname', 'lastname', 'user_name', 'phone', 'address', 'city', 'zip_code', 'profile_picture', 'is_phone_verify', 'is_identity_check', 'pays_details', 'moyenne_notes', 'avis_count']

    def get_moyenne_notes(self, obj):
        """Récupère la moyenne des avis reçus."""
        return obj.stats_notes_recues()['moyenne']

    def get_avis_count(self, obj):
        """Récupère le nombre d'avis reçus."""
        return obj.stats_notes_recues()['nombre_avis']




class MoyenPaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoyenPaiementUser
        fields = '__all__'