# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('private_key_hex', models.CharField(max_length=64, blank=True)),
                ('address', models.CharField(max_length=50, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ratio', models.FloatField()),
                ('artist', models.ForeignKey(related_name='featuring_artists', to='station.Artist')),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField()),
                ('duration', models.DurationField()),
                ('explicit', models.BooleanField(default=False)),
                ('collection', models.TextField(blank=True)),
                ('genre', models.TextField(blank=True)),
                ('subgenre', models.TextField(blank=True)),
                ('recorded_date', models.DateField()),
                ('mp3', models.FileField(null=True, upload_to=b'', blank=True)),
                ('artist', models.ForeignKey(related_name='songs', to='station.Artist')),
                ('featuring', models.ManyToManyField(to='station.Artist', through='station.Feature', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StationPlay',
            fields=[
                ('ordinal', models.IntegerField(serialize=False, primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('song', models.ForeignKey(to='station.Song')),
            ],
        ),
        migrations.AddField(
            model_name='feature',
            name='song',
            field=models.ForeignKey(related_name='featured_songs', to='station.Song'),
        ),
        migrations.AlterUniqueTogether(
            name='song',
            unique_together=set([('title', 'artist')]),
        ),
    ]
