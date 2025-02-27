from django.db import models



class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Currency(models.Model):
    code = models.CharField(max_length=10)
    symbole = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Devise'
        verbose_name_plural = 'Devises'


class Pays(models.Model):
    country_code = models.IntegerField()
    iso_code2 = models.CharField(max_length=2)
    iso_code3 = models.CharField(max_length=3)
    label = models.CharField(max_length=100)
    label_en = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='pays')
    digit_code = models.IntegerField()
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'



class Ville(models.Model):
    intitule = models.CharField(max_length=100)
    code_reference = models.IntegerField()
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name='villes')

    class Meta:
        verbose_name = 'Ville'
        verbose_name_plural = 'Villes'




class TypeBagage(models.Model):
    intitule = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'TypeBagage'
        verbose_name_plural = 'TypeBagage'




# class MoyenPaiementPlatform(models.Model):
#     type = models.CharField(max_length=50)
#     telephone = models.CharField(max_length=20)
#     numero_carte = models.CharField(max_length=16, null=True, blank=True)
#     email = models.EmailField(null=True, blank=True)
#     cvv = models.CharField(max_length=4, null=True, blank=True)
#     date_expiration = models.CharField(max_length=10, null=True, blank=True)


