# Generated by Django 3.2.25 on 2025-01-29 00:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('commons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annonce',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date_publication', models.DateTimeField(auto_now_add=True)),
                ('est_publie', models.BooleanField(default=False)),
                ('nombre_kg_dispo', models.IntegerField()),
                ('montant_par_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cout_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('commission', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('revenue_transporteur', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('est_actif', models.BooleanField(default=True)),
                ('reference', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Annonce',
                'verbose_name_plural': 'Annonces',
            },
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telephone', models.CharField(max_length=20)),
                ('numero_carte', models.CharField(blank=True, max_length=16, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('cvv', models.CharField(blank=True, max_length=4, null=True)),
                ('date_expiration', models.CharField(blank=True, max_length=10, null=True)),
                ('type', models.CharField(choices=[('MOBILE', 'MOBILE'), ('BANQUE', 'BANQUE')], default='', max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre_kg', models.IntegerField()),
                ('montant', models.DecimalField(decimal_places=2, max_digits=100)),
                ('nom_personne_a_contacter', models.CharField(max_length=100)),
                ('telephone_personne_a_contacter', models.CharField(max_length=20)),
                ('code_livraison', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('code_reception', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('reference', models.CharField(max_length=50, unique=True)),
                ('date_paiement', models.DateTimeField(null=True)),
                ('statut', models.CharField(choices=[('PENDING', 'PENDING'), ('VALIDATE', 'VALIDATE'), ('CONFIRM', 'CONFIRM'), ('RECEPTION', 'RECEPTION'), ('DELIVRATE', 'DELIVRATE'), ('CANCEL', 'CANCEL')], default='PENDING', max_length=100)),
            ],
            options={
                'verbose_name': 'Réservation',
                'verbose_name_plural': 'Réservations',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESSFUL', 'SUCCESSFUL'), ('CANCEL', 'CANCEL')], default='', max_length=12)),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
        migrations.CreateModel(
            name='Voyage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date_depart', models.DateTimeField()),
                ('agence_voyage', models.CharField(max_length=100)),
                ('code_reservation', models.CharField(max_length=100)),
                ('moyen_transport', models.CharField(choices=[('AVION', 'AVION'), ('VOITURE', 'VOITURE'), ('TRAIN', 'TRAIN')], default='PENDING', max_length=100)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='villes_dest', to='commons.ville')),
                ('provenance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='villes_prov', to='commons.ville')),
            ],
            options={
                'verbose_name': 'Voyage',
                'verbose_name_plural': 'Voyages',
            },
        ),
        migrations.CreateModel(
            name='TypeBagageReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annonce', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bagage_reservations', to='annonces.annonce')),
                ('type_bagage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='type_bagage_reservations', to='commons.typebagage')),
            ],
        ),
        migrations.CreateModel(
            name='TypeBagageAnnonce',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annonce', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bagage_annonces', to='annonces.annonce')),
                ('type_bagage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='type_bagage_annonces', to='commons.typebagage')),
            ],
        ),
    ]
