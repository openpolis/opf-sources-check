# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-30 08:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0006_content_organisation_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='content',
            old_name='meat',
            new_name='content',
        ),
    ]