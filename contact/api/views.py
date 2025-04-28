from django.utils import timezone
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from contact.models import ContactUser
from contact.api.serializers import ContactUserSerializer
from users.utils import reponses
from conf.settings import EMAIL_HOST_USER


class CreateContactUserAPIView(APIView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        try:
            contact = ContactUser.objects.get(email=request.data['email'])
            contact.last_msg_date = timezone.now()
        except ContactUser.DoesNotExist:
            contact = {
            'email': request.data['email'],
            'firstname': request.data['firstname'],
            'lastname': request.data['lastname'],
            'phone': request.data['phone']
            }
        contact_serializer = ContactUserSerializer(data=contact)
        if not ContactUserSerializer.is_valid():
            return Response(reponses(
                success=0,
                error_msg='Data requester is invalid: '+ str(ContactUserSerializer.errors),
            ))
        ctx = {
            'message': request.data['message_body']
        }
        message = render_to_string('mail_from_contact.html', ctx)
        mail = EmailMessage(
            "Contact",
            message,
            EMAIL_HOST_USER,
            [request.data['email']]
        )
        mail.content_subtype = "html"
        mail.send(fail_silently=True)
        contact_serializer.save()
        response_data = {
            **contact_serializer.data,
        }

        return Response(reponses(success=1, results=response_data))