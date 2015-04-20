import datetime

from django.db import models
from pybitcoin import BitcoinPrivateKey

# Create your models here.

song_padding = 200

class Song(models.Model):
    artist = models.ForeignKey('station.Artist')
    title = models.TextField()
    duration = models.DurationField()
    explicit = models.BooleanField(default=False)
    genre = models.TextField(blank=True)
    subgenre= models.TextField(blank=True)
    recorded_date = models.DateField()

    mp3 = models.FileField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.artist.name, self.title)

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

        title_repeat = int(Song.objects.count() / 2)
        artist_repeat = int(Artist.objects.count() / 2)

        last_artists = StationPlay.objects.order_by('-ordinal')[:artist_repeat]
        plays_last_title = StationPlay.objects.order_by('-ordinal')[:title_repeat]

        if self.artist in [x.song.artist for x in last_artists]:
            return False
        if self.title in [x.song.title for x in plays_last_title]:
            return False
        return True


class Artist(models.Model):
    name = models.TextField(unique=True)
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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s - %s" % (self.start_time, self.song, self.end_time)

    @classmethod
    def generate_next(cls, last_end):
        for x in xrange(Song.objects.count()):
            random_song = Song.objects.exclude(mp3='').order_by("?")[0]
            if random_song.is_valid_next():
                chosen_song = random_song
                start = last_end
                end = start + chosen_song.duration + datetime.timedelta(seconds=2)
                return cls.objects.create(
                    song=chosen_song,
                    start_time=start,
                    end_time=end,
                )
        raise Exception("No eligible songs")

    def as_dict(self):
        return {
            'artist': self.song.artist.name,
            'bitcoin': self.song.artist.address,
            'title': self.song.title,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.song.duration.total_seconds(),
            'url': self.song.mp3.url
        }
