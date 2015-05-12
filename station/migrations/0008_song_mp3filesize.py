# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0007_song_retired'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='mp3filesize',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
    ]
