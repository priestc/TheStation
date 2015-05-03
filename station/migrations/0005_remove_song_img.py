# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0004_song_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='img',
        ),
    ]
