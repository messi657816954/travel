# Generated by Django 3.2.25 on 2025-01-29 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonces', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annonce',
            name='type_bagage_auto',
        ),
        migrations.AlterField(
            model_name='voyage',
            name='moyen_transport',
            field=models.CharField(choices=[('AVION', 'AVION'), ('VOITURE', 'VOITURE'), ('TRAIN', 'TRAIN')], default='', max_length=100),
        ),
    ]
