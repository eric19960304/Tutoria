# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-08 13:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20171108_2059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tutor',
            old_name='tags',
            new_name='tag',
        ),
    ]
