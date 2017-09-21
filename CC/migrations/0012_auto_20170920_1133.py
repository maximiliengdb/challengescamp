# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-09-20 09:33
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CC', '0011_auto_20170919_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualite',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 20, 11, 33, 51, 965148)),
        ),
        migrations.AlterField(
            model_name='defi',
            name='date_envoie',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 20, 11, 33, 51, 965148)),
        ),
        migrations.AlterField(
            model_name='maj',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 20, 11, 33, 51, 965148)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 20, 11, 33, 51, 965148)),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='derniere_connexion',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 20, 11, 33, 51, 965148)),
        ),
    ]
