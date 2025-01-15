from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Pays(models.Model):
    intitule = models.CharField(max_length=100)
    code_reference = models.CharField(max_length=10)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'

class Ville(models.Model):
    intitule = models.CharField(max_length=100)
    code_reference = models.CharField(max_length=10)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name='villes')

    class Meta:
        verbose_name = 'Ville'
        verbose_name_plural = 'Villes'

class Currency(models.Model):
    code = models.CharField(max_length=3)
    symbole = models.CharField(max_length=5)

    class Meta:
        verbose_name = 'Devise'
        verbose_name_plural = 'Devises'
