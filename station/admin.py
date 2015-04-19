from django.contrib import admin

# Register your models here.

from .models import Artist, Song, StationPlay

admin.site.register(StationPlay)
admin.site.register(Song)
admin.site.register(Artist)
