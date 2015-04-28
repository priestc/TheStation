# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0002_auto_20150426_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feature',
            name='ratio',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
