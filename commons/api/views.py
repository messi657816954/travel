from rest_framework.views import APIView
from rest_framework.permissions import *
from rest_framework.response import Response

from users.utils import reponses
from .serializers import  TypeBagageSerializer, VilleSerializer, PaysSerializer, \
    CurrencySerializer
from ..models import TypeBagage, Ville, Pays, Currency
from rest_framework import generics,status


class CurrencyListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CurrencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_201_CREATED)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class CurrencyDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Currency.objects.get(pk=pk)
        except Currency.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        currency = self.get_object(pk)
        if not currency:
            res = reponses(success=0, error_msg="Devise introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = CurrencySerializer(currency)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        currency = self.get_object(pk)
        if not currency:
            res = reponses(success=0, error_msg="Devise introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = CurrencySerializer(currency, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_200_OK)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        currency = self.get_object(pk)
        if not currency:
            res = reponses(success=0, error_msg="Devise introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        currency.delete()
        res = reponses(success=1, results="Devise supprimée avec succès.", error_msg='')
        return Response(res, status=status.HTTP_204_NO_CONTENT)


class PaysListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        pays = Pays.objects.filter(active=True).order_by("label")
        serializer = PaysSerializer(pays, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = PaysSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_201_CREATED)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class PaysDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Pays.objects.get(pk=pk)
        except Pays.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        pays = self.get_object(pk)
        if not pays:
            res = reponses(success=0, error_msg="Pays introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = PaysSerializer(pays)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        pays = self.get_object(pk)
        if not pays:
            res = reponses(success=0, error_msg="Pays introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = PaysSerializer(pays, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_200_OK)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        pays = self.get_object(pk)
        if not pays:
            res = reponses(success=0, error_msg="Pays introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        pays.delete()
        res = reponses(success=1, results="Pays supprimé avec succès.", error_msg='')
        return Response(res, status=status.HTTP_204_NO_CONTENT)


class VilleListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if 'pays_id' in request.query_params:
            villes = Ville.objects.filter(pays__pk=request.query_params['pays_id'])
            serializer = VilleSerializer(villes, many=True)
            print('serializer.data', serializer.data)
            res = reponses(success=1, results=serializer.data)
            return Response(res)
        return Response(reponses(success=0, error_msg="Spécifiez l'identifiant du pays!"))


    def post(self, request, *args, **kwargs):
        serializer = VilleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_201_CREATED)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class VilleDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Ville.objects.get(pk=pk)
        except Ville.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        ville = self.get_object(pk)
        if not ville:
            res = reponses(success=0, error_msg="Ville introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = VilleSerializer(ville)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        ville = self.get_object(pk)
        if not ville:
            res = reponses(success=0, error_msg="Ville introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = VilleSerializer(ville, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_200_OK)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        ville = self.get_object(pk)
        if not ville:
            res = reponses(success=0, error_msg="Ville introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        ville.delete()
        res = reponses(success=1, results="Ville supprimée avec succès.", error_msg='')
        return Response(res, status=status.HTTP_204_NO_CONTENT)


class TypeBagageListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        types = TypeBagage.objects.all()
        serializer = TypeBagageSerializer(types, many=True)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = TypeBagageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_201_CREATED)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class TypeBagageDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return TypeBagage.objects.get(pk=pk)
        except TypeBagage.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        type_bagage = self.get_object(pk)
        if not type_bagage:
            res = reponses(success=0, error_msg="Type de bagage introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = TypeBagageSerializer(type_bagage)
        res = reponses(success=1, results=serializer.data, error_msg='')
        return Response(res, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        type_bagage = self.get_object(pk)
        if not type_bagage:
            res = reponses(success=0, error_msg="Type de bagage introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        serializer = TypeBagageSerializer(type_bagage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            res = reponses(success=1, results=serializer.data, error_msg='')
            return Response(res, status=status.HTTP_200_OK)
        res = reponses(success=0, error_msg=serializer.errors)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        type_bagage = self.get_object(pk)
        if not type_bagage:
            res = reponses(success=0, error_msg="Type de bagage introuvable.")
            return Response(res, status=status.HTTP_404_NOT_FOUND)
        type_bagage.delete()
        res = reponses(success=1, results="Type de bagage supprimé avec succès.", error_msg='')
        return Response(res, status=status.HTTP_204_NO_CONTENT)
