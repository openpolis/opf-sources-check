# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-29 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='use the sequence IT - Name, where: I-Institution [C|G], T-type[R|P|C], Name, i.e. CR - Lazio)', max_length=250, verbose_name='the identifier of the url')),
                ('url', models.URLField()),
                ('xpath', models.CharField(blank=True, max_length=250)),
                ('regexp', models.CharField(blank=True, max_length=250)),
                ('meat', models.TextField(blank=True, verbose_name='Meaningful content')),
                ('notes', models.TextField(blank=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('verification_status', models.IntegerField(choices=[(1, 'changed'), (0, 'unchanged'), (2, 'with errors')], default=0)),
                ('verification_error', models.CharField(blank=True, max_length=250)),
                ('todo', models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
    ]
