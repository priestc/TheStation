# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('station', '0005_remove_song_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='image',
            field=models.ImageField(upload_to=b'', blank=True),
        ),
    ]
