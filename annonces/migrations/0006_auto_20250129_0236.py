# Generated by Django 3.2.25 on 2025-01-29 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonces', '0005_auto_20250129_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='paiement',
            name='type_paiement',
            field=models.CharField(choices=[('MOBILE', 'MOBILE'), ('BANQUE', 'BANQUE')], default='', max_length=12),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='type',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESSFUL', 'SUCCESSFUL'), ('FAILED', 'FAILED')], default='', max_length=12),
        ),
    ]
