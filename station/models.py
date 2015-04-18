import datetime
from django.db import models

# Create your models here.

class Song(models.Model):
    artist = models.ForeignKey('station.Artist')
    title = models.TextField()
    duration = models.
    explicit = models.BooleanField(defalt=False)
    url = models.TextField()

    def last_played(self):
        """
        When the last
        """
        return self.stationplay_set.latest().played

class Artist(models.Model):
    name = models.TextField()
    bitcoin_address = models.TextField()

    def __unicode__(self):
        return self.name

    def address(self):
        if not self.bitcoin_address:
            self.bitcoin_address = generate_address()
            self.save()

        return self.bitcoin_address

class StationPlay(models.Model):
    ordinal = models.IntgerField(primary_key=True)
    song = models.ForeignKey('station.Song')
    played = models.DateTimeField(default=datetimedatetime.now)

    class Meta:
        get_latest_by = 'played'
