import datetime
import random
import requests
import urllib2

import pytz
from django.db import models
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from pybitcoin import BitcoinPrivateKey
from django.conf import settings

# seconds to schedule between songs
SONG_PADDING = 2

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

    image = models.ImageField(blank=True)

    class Meta:
        unique_together = (("title", "artist"),)

    def __unicode__(self):
        return "%s - %s%s" % (self.artist.name, self.title, self.feat())

    def fetch_from_lastfm(self):
        url = "http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=%s&artist=%s&track=%s&format=json" % (
            settings.LASTFM_KEY, self.artist.name, "%s %s" % (self.title, self.feat)
        )
        return requests.get(url).json()

    def fetch_img(self):
        response = self.fetch_from_lastfm()
        imgsrc = response['track']['album']['image'][3]['#text']
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(imgsrc).read())
        img_temp.flush()
        self.image = File(img_temp)
        self.save()

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

    def estimate_bitrate_kbps(self):
        """
        Calculate approximate bitrate based on filesize and duration.
        Returns a number that is kilobits / second.
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

    def is_valid_next(self, last_song):
        """
        Is this song eligible to be the next song in the station?
        Determine this by comparing it with the
        """
        if not self.image:
            return False

        if self.genre and self.genre == last_song.genre:
            return False

        if self.collection and last_song.collection == self.collection:
            return False

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

    def is_verified(self):
        """
        Verified means the artist itself has control over the private key,
        therefore, in this database, the private key is not known.
        """
        return not bool(self.private_key_hex)

    def generate_address(self, force=False):
        if self.address and not force:
            return

        if not settings.ARTIST_DONATE_ADDRESS_SOURCE:
            # No donate address has been given in settings
            # this means we generate a unique one and store the private key
            # along with it. It is the responsibility of the maintainer
            # if this installation to make sure the private key is distributed
            # to the artist.

            priv = BitcoinPrivateKey()
            self.private_key_hex = priv.to_hex()
            self.address = priv.public_key().address()
            self.save()
        else:
            # point to another installation of TheStation to get the correct
            # donate address.
            url = (
                "http://" + settings.ARTIST_DONATE_ADDRESS_SOURCE +
                "/get_artist_donate_address" +
                "?artist=%s" % self.name
            )
            self.address = requests.get(url).json()['donate_address']
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
    def average_bandwidth_kbps(cls):
        """
        Returns the average kilobits per second for all songs in the library.
        """
        data = [x.estimate_bitrate_kbps() for x in Song.objects.all()]
        return sum(data) / len(data)

    @classmethod
    def average_duration_minutes(cls):
        """
        Calculate the average number of minutes each song is in the song library.
        """
        data = [x.duration.total_seconds() for x in Song.objects.all()]
        return sum(data) / len(data) / 60

    @classmethod
    def average_bytes_per_song(cls):
        """
        The Average bytes of bandwidth used per song.
        """
        return (cls.average_bandwidth_kbps() * 60 * 8) * cls.average_duration_minutes()

    @classmethod
    def cost_per_song_per_user_usd(cls):
        gb_per_song = cls.average_bytes_per_song() / 1024 / 1024 / 1024
        cost_per_gb = 0.09 # according to Amazon S3 pricing page.
        return gb_per_song * cost_per_gb

    @classmethod
    def generate_next(cls, last_end):
        try:
            last_song = StationPlay.objects.latest('ordinal').song
        except StationPlay.DoesNotExist:
            # this is the first song of this station's history. Generate a
            # previous song to satisify the algorithm.
            now = datetime.datetime.now(pytz.utc)
            one_time_random_song = Song.objects.order_by("?")[0]
            last_play = StationPlay.objects.create(
                song=one_time_random_song,
                start_time=now - (one_time_random_song.duration + datetime.timedelta(seconds=SONG_PADDING)),
                end_time=now
            )
            last_song = last_play.song

        random_songs = Song.objects.exclude(mp3='').order_by("?")
        j = 0

        chosen_song = None
        for i, random_song in enumerate(random_songs):
            if random_song.is_valid_next(last_song):
                # randomly try each song until an eligible one is found
                chosen_song = random_song
                break;
        else:
            # no eligible songs, return any song, except the one that was just played
            for j, random_song in enumerate(random_songs):
                if random_song != last_song:
                    chosen_song = random_song
                    break;

        start = last_end
        end = start + chosen_song.duration + datetime.timedelta(seconds=SONG_PADDING)

        return cls.objects.create(
            song=chosen_song,
            start_time=start,
            end_time=end,
        ), i + j

    def as_dict(self):
        return {
            'artist': self.song.artist.name,
            'tips': self.song.get_tips(),
            'title': self.song.title + self.song.feat(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': self.song.duration.total_seconds(),
            'url': self.song.mp3.url,
            'year': self.song.recorded_date.strftime("%Y"),
            "img": self.song.image.url
        }
