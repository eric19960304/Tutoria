# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-23 05:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20171123_1345'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='isSystemRelated',
            new_name='isSystemWalletRelated',
        ),
    ]
