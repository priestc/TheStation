import datetime
from django.db import models

# Create your models here.

class Song(models.Model):
    artist = models.ForeignKey('station.Artist')
    title = models.TextField()
    duration = models.DurationField()
    explicit = models.BooleanField(default=False)
    genre = models.TextField()
    subgenre= models.TextField()
    recorded_date = models.DateField()

    url = models.TextField()

    def last_played(self):
        """
        When the last time his song was played
        """
        return self.stationplay_set.latest().played

    def is_valid_next(self):
        """
        Is this song eligible to be the next song in the station?
        Determine this by comparing it with the
        """
        last_twenty = SongPlay.objects.order_by('-ordinal')[:20]
        last_five = last_twenty[:5]

        if self.artist in [x.artist for x in last_20]:
            return False
        if self.genre in [x.genre for x in last_five]:
            return False
        return True


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
    ordinal = models.IntegerField(primary_key=True)
    song = models.ForeignKey('station.Song')
    playtime = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        get_latest_by = 'played'

    @classmethod
    def generate_next(cls):
        while True:
            random_song = Song.objects.order_by("?")[0]
            if random_song.is_valid_next():
                last_song = cls.objects.latest()
                last_start = last_song.playtime
                return cls.objects.create(
                    song=random_song,
                    playtime=last_start + random_song.duration
                )
