# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-11 14:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20171111_2208'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviewtutortempurl',
            old_name='url_hash',
            new_name='temp_url',
        ),
    ]
