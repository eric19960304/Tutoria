# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-11 18:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_reviewtempurl_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='used_date',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='used_session',
        ),
    ]
