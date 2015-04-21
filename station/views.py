import datetime
import pytz

import eyed3

from django.shortcuts import render
from django.http import JsonResponse

from .models import StationPlay, Artist, Song

def current_and_next_song(request):
    now = datetime.datetime.now(pytz.utc)

    try:
        current_play = StationPlay.objects.get(start_time__lt=now, end_time__gt=now)
    except StationPlay.DoesNotExist:
        # no current_play == station went dead due to no listeners
        current_play = StationPlay.generate_next(now)

    try:
        next_play = StationPlay.objects.get(start_time__gt=now)
    except StationPlay.DoesNotExist:
        # first hit after a new generated song, generate the next song.
        next_play = StationPlay.generate_next(current_play.end_time)

    return JsonResponse({
        'current_song': current_play.as_dict(),
        'next_song': next_play.as_dict(),
    })

def player(request):
    return render(request, "home.html", {})

def upload(request):
    if request.POST:
        f = request.FILES['file']
        path = f.temporary_file_path()
        mp3 = eyed3.load(path)

        artist, c = Artist.objects.get_or_create(
            name=mp3.tag.artist
        )

        try:
            year = mp3.tag.getBestDate().year
        except:
            year = year=int(request.POST['year'])

        date = datetime.datetime(year=year, day=1, month=1)

        Song.objects.create(
            artist=artist,
            title=mp3.tag.title,
            collection=mp3.tag.album,
            duration=datetime.timedelta(seconds=mp3.info.time_secs),
            genre=mp3.tag.genre or "",
            recorded_date=date,
            mp3=f,
        )

    return render(request, "upload.html", {})
