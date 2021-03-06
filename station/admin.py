import datetime
import pytz

from django.contrib import admin
from django.conf import settings

from .models import Artist, Song, StationPlay, Feature
from .forms import SongFormImageURL

class FeatureInline(admin.TabularInline):
    model = Feature


def donate_address(modeladmin, request, queryset):
    for artist in queryset:
        if not artist.address:
            artist.generate_address()

if settings.ARTIST_DONATE_ADDRESS_SOURCE:
    donate_address.short_description = "Fetch Donate Address"
else:
    donate_address.short_description = "Generate Donate Address"

def fetch_album_art(modeladmin, request, queryset):
    for song in queryset:
        try:
            song.fetch_img()
        except:
            pass


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'song_count', 'play_count', 'tipped_value')
    actions = [donate_address]
    exclude = ('private_key_hex', )
    search_fields = ('name', )
    #readonly_fields = ('private_key_wif', )

    def song_count(self, obj):
        return obj.songs.count()

    def play_count(self, obj):
        return StationPlay.objects.filter(song__artist=obj).count()

    def tipped_value(self, obj):
        tips = obj.get_tipped_value()
        if tips > 0:
            return "<b>$%.2f</b>" % tips
        else:
            return "$0"
    tipped_value.allow_tags = True


class SongAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'artist_with_featuring', 'year', 'collection', 'duration',
        'has_mp3', 'last_played_ago', 'times_played', 'has_image', 'mp3filesize',
        'bitrate'
    )
    actions = [fetch_album_art]
    inlines = [FeatureInline]
    readonly_fields = ('picture', )
    search_fields = ['title', 'artist__name', 'collection']
    #filter_horizontal = ['has_image']
    form = SongFormImageURL

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True

    def picture(self, obj):
        if not obj.image:
            return "None"
        return "<img src='%s' height=300 length=300>" % obj.image.url
    picture.allow_tags = True

    def bitrate(self, obj):
        return "%d kbps" % obj.estimate_bitrate_kbps()

    def artist_with_featuring(self, obj):
        feat = obj.feat()
        return "%s<span style='color: blue'>%s</span>" % (obj.artist.name, feat)
    artist_with_featuring.allow_tags = True
    artist_with_featuring.admin_order_field = 'artist__name'

    def year(self, obj):
        return obj.recorded_date.strftime("%Y")

    def has_mp3(self, obj):
        return bool(obj.mp3)
    has_mp3.boolean = True

    def times_played(self, obj):
        return obj.stationplay_set.count()


class StationPlayAdmin(admin.ModelAdmin):
    list_display = ('ordinal', 'playing', 'start_admin', 'end_admin', 'identicon', 'song', 'duration', 'played_ago')

    def duration(self, obj):
        return obj.song.duration

    def start_admin(self, obj):
        return obj.start_time.astimezone(pytz.timezone('US/Pacific')).strftime("%B %d %Y %I:%M:%S %p %Z")
    start_admin.short_description = 'Start'

    def end_admin(self, obj):
        return obj.end_time.astimezone(pytz.timezone('US/Pacific')).strftime("%B %d %Y %I:%M:%S %p %Z")
    end_admin.short_description = 'End'

    def playing(self, obj):
        return obj.start_time < datetime.datetime.now(pytz.utc) < obj.end_time
    playing.boolean = True

    def identicon(self, obj):
        id = obj.start_time.microsecond
        url = "http://www.gravatar.com/avatar/%s?d=identicon" % id
        return "<img src='%s' height='20px'>" % url
    identicon.allow_tags = True

admin.site.register(StationPlay, StationPlayAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Artist, ArtistAdmin)
