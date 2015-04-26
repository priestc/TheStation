# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationplay',
            name='ordinal',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
