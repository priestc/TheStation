import datetime
import pytz

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from .models import StationPlay, Artist, Song
from .forms import NewSongForm

def current_and_next_song(request):
    now = datetime.datetime.now(pytz.utc)

    try:
        current_play = StationPlay.objects.get(start_time__lt=now, end_time__gt=now)
    except StationPlay.DoesNotExist:
        # no current_play == station went dead due to no listeners
        current_play, tries = StationPlay.generate_next(now)

    try:
        next_play = StationPlay.objects.get(start_time__gt=now)
    except StationPlay.DoesNotExist:
        # first hit after a new generated song, generate the next song.
        next_play, tries = StationPlay.generate_next(current_play.end_time)
        print "Generated new track, tried this many times:", tries

    return JsonResponse({
        'current_song': current_play.as_dict(),
        'next_song': next_play.as_dict(),
    })

def player(request):
    return render(request, "home.html", {})

@login_required
def upload(request):
    form = NewSongForm()
    if request.POST:
        form = NewSongForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            url = reverse("upload")
            return HttpResponseRedirect(url)

    return render(request, "upload.html", locals())
