from django.db import models
from django.utils import timezone


class ContactUser(models.Model):

    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, null=True, blank=True)
    last_msg_date = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name = 'ContactUser'
        verbose_name_plural = 'ContactUsers'