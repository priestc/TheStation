import datetime
from django.db import models
from pybitcoin import BitcoinPrivateKey

# Create your models here.

class Song(models.Model):
    artist = models.ForeignKey('station.Artist')
    title = models.TextField()
    duration = models.DurationField()
    explicit = models.BooleanField(default=False)
    genre = models.TextField(blank=True)
    subgenre= models.TextField(blank=True)
    recorded_date = models.DateField()

    mp3 = models.FileField(null=True, blank=True)

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
    private_key_hex = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return self.name

    def generate_address(self):
        if not self.address:
            priv = BitcoinPrivateKey()
            self.private_key_hex = priv.to_hex()
            self.address = priv.public_key().address()
            self.save()

        return self.address

    def private_key_wif(self):
        return BitcoinPrivateKey(self.private_key_hex).to_wif()

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
