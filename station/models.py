import datetime
import random

import pytz
from django.db import models
from pybitcoin import BitcoinPrivateKey

# Create your models here.

song_padding = 200

class Feature(models.Model):
    song = models.ForeignKey('station.Song', related_name='featured_songs')
    artist = models.ForeignKey('station.Artist', related_name='featuring_artists')
    ratio = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return "feat. %s" % self.artist.name

class Song(models.Model):
    artist = models.ForeignKey('station.Artist', related_name='songs')
    title = models.TextField()
    duration = models.DurationField()
    explicit = models.BooleanField(default=False)
    collection = models.TextField(blank=True)
    genre = models.TextField(blank=True)
    subgenre= models.TextField(blank=True)
    recorded_date = models.DateField()
    featuring = models.ManyToManyField('station.Artist', through='station.Feature', blank=True)

    mp3 = models.FileField(null=True, blank=True)

    class Meta:
        unique_together = (("title", "artist"),)

    def __unicode__(self):
        return "%s - %s%s" % (self.artist.name, self.title, self.feat())

    def feat(self):
        """
        Make the little "feat" tag to put at the end of the title of the song
        has featuring artists. This function handles putting the commas and
        amperstand depending on how many features there are.
        """
        featuring = list(self.featuring.all())

        if not featuring:
            return ""

        if len(featuring) == 1:
            return " (feat. %s)" % featuring[0].name
        elif len(featuring) == 2:
            return " (feat. %s & %s)" % tuple([x.name for x in featuring])

        last_two = "%s & %s" % tuple([x.name for x in featuring[-2:]])
        return " (feat. %s, %s)" % (
            " ,".join([x.name for x in featuring[:-2]]), last_two
        )

    def estimate_bitrate(self):
        """
        Calculat approximate bitrate based on
        """
        return ((self.mp3.size / 1024) * 8) / self.duration.total_seconds()

    def get_tips(self):
        """
        Always returns a list of dicts, each dict containing all the data needed
        to make the microtip meta tags, or microtip audio tag.
        """
        if self.featuring.exists():
            feature_tips = []
            all_features = list(Feature.objects.filter(song=self))
            share = 0.5 / len(all_features)
            for feature in all_features:
                feature_tips.append({
                    'recipient': feature.artist.name,
                    'ratio': feature.ratio or share,
                    'address': feature.artist.address,
                })
            return feature_tips + [{
                'recipient': self.artist.name,
                'ratio': 0.5,
                'address': self.artist.address,
            }]

        return [{
            'recipient': self.artist.name,
            'ratio': 1.0,
            'address': self.artist.address,
        }]

    @property
    def last_played(self):
        """
        When the last time his song was played.
        """
        return self.stationplay_set.latest('ordinal').start_time

    @property
    def last_played_ago(self):
        return datetime.datetime.now(pytz.utc) - self.last_played

    def is_valid_next(self):
        """
        Is this song eligible to be the next song in the station?
        Determine this by comparing it with the
        """

        title_repeat = int(Song.objects.count() / 2)
        artist_repeat = int(Artist.objects.count() / 3)

        last_artists = StationPlay.objects.order_by('-ordinal')[:artist_repeat]
        plays_last_title = StationPlay.objects.order_by('-ordinal')[:title_repeat]

        if self.artist in [x.song.artist for x in last_artists]:
            return False
        if self.title in [x.song.title for x in plays_last_title]:
            return False
        return True


class Artist(models.Model):
    name = models.TextField(unique=True)
    private_key_hex = models.CharField(max_length=64, blank=True)
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
    ordinal = models.AutoField(primary_key=True)
    song = models.ForeignKey('station.Song')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s - %s" % (self.start_time, self.song, self.end_time)

    @classmethod
    def average_bandwidth(cls):
        data = [x.estimate_bitrate() for x in Song.objects.all()]
        return sum(data) / len(data)

    @classmethod
    def average_duration(cls):
        data = [x.duration.total_seconds() for x in Song.objects.all()]
        return sum(data) / len(data)

    @classmethod
    def generate_next(cls, last_end):
        chosen_song = None
        for i, random_song in enumerate(Song.objects.exclude(mp3='').order_by("?")):
            if random_song.is_valid_next():
                chosen_song = random_song
                break;
        else:
            chosen_song = random_song

        start = last_end
        end = start + chosen_song.duration + datetime.timedelta(seconds=2)

        return cls.objects.create(
            song=chosen_song,
            start_time=start,
            end_time=end,
        ), i

    def as_dict(self):
        return {
            'artist': self.song.artist.name,
            'tips': self.song.get_tips(),
            'title': self.song.title + self.song.feat(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.song.duration.total_seconds(),
            'url': self.song.mp3.url,
            'year': self.song.recorded_date.strftime("%Y"),
        }
