from django.shortcuts import render

# Create your views here.

def current_and_next_song(request):
    current = StationPlay.objects.latest()

def player(request):
    return render(request, "home.html", {})
