from users.models import User
from django.db import models
from commons.models import Currency

class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)
    active = models.BooleanField()

    def __str__(self):
        return self.name

class UserPreference(models.Model):
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]

    COMMUNICATION_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('none', 'Aucune'),
    ]

    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    communication = models.CharField(max_length=10, choices=COMMUNICATION_CHOICES, default='email')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Preferences of {self.user_id.username}"
