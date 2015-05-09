# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0006_song_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='retired',
            field=models.BooleanField(default=False),
        ),
    ]
