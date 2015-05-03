# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0003_auto_20150428_0116'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='img',
            field=models.URLField(blank=True),
        ),
    ]
