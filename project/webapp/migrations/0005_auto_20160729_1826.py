# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-29 16:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_auto_20160729_1156'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganisationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='Denominazione')),
            ],
            options={
                'verbose_name': 'tipo di organizzazione',
                'verbose_name_plural': 'tipi di organizzazione',
            },
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(help_text='usare la sequenza IT - Nome, dove: I-Istituzione\n                     [C|G], T-tipo[R|P|C], Nome (es. CR - Lazio)', max_length=250, verbose_name='Denominazione della fonte'),
        ),
    ]
