import datetime
import pytz
import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import StationPlay, Artist, Song
from .forms import UploadSongForm

def get_current_and_next_play():
    now = datetime.datetime.now(pytz.utc)

    try:
        current_play = StationPlay.objects.get(start_time__lt=now, end_time__gt=now)
    except StationPlay.DoesNotExist:
        # no current_play == station went dead due to no listeners
        current_play, tries = StationPlay.generate_next(now)
    except StationPlay.MultipleObjectsReturned:
        # keep the first, delete the second duplicate
        sp = StationPlay.objects.filter(start_time__lt=now, end_time__gt=now)
        current_play = sp[0]
        [x.delete() for x in sp[1:]]

    try:
        next_play = StationPlay.objects.get(start_time__gt=now)
    except StationPlay.DoesNotExist:
        # first hit after a new generated song, generate the next song.
        next_play, tries = StationPlay.generate_next(current_play.end_time)
        print "Generated new track, tried this many times:", tries

    next_fetch = next_play.start_time + (next_play.song.duration / 2)

    return current_play, next_play, next_fetch

def current_and_next_song(request):
    """
    View to handle the API call for getting the next and currently playing
    song.
    """
    current_play, next_play, next_fetch = get_current_and_next_play()
    return JsonResponse({
        'current_song': current_play.as_dict(),
        'next_song': next_play.as_dict(),
        'next_fetch': next_fetch,
    })

def player(request, autoplay=False):
    """
    This view handles making the main audio player page. Aka the home page.
    """
    current_play, next_play, next_fetch = get_current_and_next_play()
    return render(request, "home.html", {
        'current_play': current_play.as_dict(),
        'next_play': next_play.as_dict(),
        'autoplay': autoplay,
        'TITLE': settings.TITLE,
        'BANDWIDTH_FUND_ADDRESS': settings.BANDWIDTH_FUND_ADDRESS,
        'next_fetch': next_fetch,
        'next_play_json': json.dumps(next_play.as_dict()), # django should have a built-in json template tag
        'current_play_tips_json': json.dumps(current_play.as_dict()['tips']),
    })

@login_required
def upload(request):
    """
    A very basic MP3 uploader form.
    """
    form = UploadSongForm()
    if request.POST:
        form = UploadSongForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            url = reverse("upload")
            return HttpResponseRedirect(url)

    LASTFM_KEY = settings.LASTFM_KEY
    return render(request, "upload.html", locals())

def get_artist_donate_address(request):
    """
    Most likely this view is being called by another installation of TheStation
    We return the donate address of the artist passed in.
    """
    if not settings.SERVE_ADDRESSES:
        raise HttpResponseForbidden("Not enabled")

    artist_name = request.GET['artist']
    try:
        artist = Artist.objects.get(name__iexact=artist_name)
    except Artist.DoesNotExist:
        artist = Artist.objects.create(name=artist_name)
        artist.generate_address()

    return JsonResponse({
        'donate_address': artist.address,
        'verified': artist.is_verified()
    })

def station_stats(request):
    return JsonResponse({
        'total_songs': Song.eligible_for_broadcast().count(),
        'average_bitrate_kbps': StationPlay.average_bandwidth_kbps(),
        'average_duration_minutes': StationPlay.average_duration_minutes(),
        'average_bytes_per_song': StationPlay.average_bytes_per_song(),
        'average_bytes_per_minute': StationPlay.average_bytes_per_minute(),
        'bandwidth_cost_per_song_usd': StationPlay.cost_per_song_per_user_usd(),
        'bandwidth_cost_per_minute_usd': StationPlay.cost_per_minute_per_user_usd()
    })
