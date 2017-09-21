# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-09-19 08:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CC', '0010_auto_20170919_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposition_Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(default='Sans Titre', max_length=255)),
                ('description', models.CharField(default='Sans Titre', max_length=5000)),
                ('latitude', models.FloatField(default=0)),
                ('longitude', models.FloatField(default=0)),
                ('etat', models.CharField(choices=[('E', 'Envoyé'), ('D', 'Default'), ('V', 'Validé'), ('S', 'Signalé')], default='E', max_length=2)),
            ],
        ),
        migrations.AlterField(
            model_name='actualite',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 19, 10, 58, 9, 904826)),
        ),
        migrations.AlterField(
            model_name='defi',
            name='date_envoie',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 19, 10, 58, 9, 904826)),
        ),
        migrations.AlterField(
            model_name='maj',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 19, 10, 58, 9, 904826)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 19, 10, 58, 9, 904826)),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='derniere_connexion',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 19, 10, 58, 9, 904826)),
        ),
        migrations.AddField(
            model_name='proposition_point',
            name='auteur',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CC.Utilisateur'),
        ),
    ]