from django.db import models

from commons.models import TimeStampedModel


class Notification(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    est_lu = models.BooleanField(default=False)
    type = models.CharField(max_length=50)  # email, sms, in-app

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
