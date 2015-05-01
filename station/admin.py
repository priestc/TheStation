import datetime
import pytz

from django.contrib import admin

# Register your models here.

from .models import Artist, Song, StationPlay, Feature

class FeatureInline(admin.TabularInline):
    model = Feature


def generate_address(modeladmin, request, queryset):
    for artist in queryset:
        if not artist.address:
            artist.generate_address()


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'song_count')
    actions = [generate_address]
    exclude = ('private_key_hex', )
    #readonly_fields = ('private_key_wif', )

    def song_count(self, obj):
        return obj.songs.count()

class SongAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'artist_with_featuring', 'year', 'collection', 'duration',
        'has_mp3', 'last_played_ago', 'times_played', 'bitrate'
    )

    inlines = [
        FeatureInline
    ]

    def bitrate(self, obj):
        return "%d kbps" % obj.estimate_bitrate()

    def artist_with_featuring(self, obj):
        feat = obj.feat()
        return "%s<span style='color: blue'>%s</span>" % (obj.artist.name, feat)
    artist_with_featuring.allow_tags = True

    def year(self, obj):
        return obj.recorded_date.strftime("%Y")

    def has_mp3(self, obj):
        return bool(obj.mp3)
    has_mp3.boolean = True

    def times_played(self, obj):
        return obj.stationplay_set.count()


class StationPlayAdmin(admin.ModelAdmin):
    list_display = ('ordinal', 'playing', 'starttime', 'endtime2', 'song', 'duration', 'played_ago')

    def duration(self, obj):
        return obj.song.duration

    def starttime(self, obj):
        return obj.start_time.strftime("%B %d %Y %H:%M:%S.%f")

    def endtime2(self, obj):
        return obj.end_time.strftime("%B %d %Y %H:%M:%S.%f")

    def playing(self, obj):
        return obj.start_time < datetime.datetime.now(pytz.utc) < obj.end_time
    playing.boolean = True

    def played_ago(self, obj):
        return obj.song.last_played_ago

admin.site.register(StationPlay, StationPlayAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Artist, ArtistAdmin)
