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
    list_display = ('name', 'address')
    actions = [generate_address]
    exclude = ('private_key_hex', )
    #readonly_fields = ('private_key_wif', )


class SongAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'artist', 'year', 'collection', 'genre', 'subgenre',
        'has_mp3', 'last_played_ago', 'times_played'
    )

    inlines = [
        FeatureInline
    ]

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
        return obj.song.duration.total_seconds()

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
