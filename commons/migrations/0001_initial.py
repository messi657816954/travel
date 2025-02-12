# Generated by Django 3.2.25 on 2025-01-29 00:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('symbole', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name': 'Devise',
                'verbose_name_plural': 'Devises',
            },
        ),
        migrations.CreateModel(
            name='Pays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intitule', models.CharField(max_length=100)),
                ('code_reference', models.CharField(max_length=10)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pays', to='commons.currency')),
            ],
            options={
                'verbose_name': 'Pays',
                'verbose_name_plural': 'Pays',
            },
        ),
        migrations.CreateModel(
            name='TypeBagage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intitule', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'TypeBagage',
                'verbose_name_plural': 'TypeBagage',
            },
        ),
        migrations.CreateModel(
            name='Ville',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intitule', models.CharField(max_length=100)),
                ('code_reference', models.CharField(max_length=10)),
                ('pays', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='villes', to='commons.pays')),
            ],
            options={
                'verbose_name': 'Ville',
                'verbose_name_plural': 'Villes',
            },
        ),
    ]
