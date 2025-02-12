# Generated by Django 3.2.25 on 2025-01-29 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annonces', '0006_auto_20250129_0236'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paiement',
            name='type_paiement',
        ),
        migrations.AddField(
            model_name='paiement',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESSFUL', 'SUCCESSFUL'), ('FAILED', 'FAILED')], default='', max_length=12),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='type',
            field=models.CharField(choices=[('MOBILE', 'MOBILE'), ('BANQUE', 'BANQUE')], default='', max_length=12),
        ),
    ]
