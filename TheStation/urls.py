import django
from django.conf.urls import patterns, include, url
from django.contrib import admin
from station import views
from django.conf import settings

urlpatterns = [
    # Examples:
    # url(r'^$', 'TheStation.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^current_and_next_song$', views.current_and_next_song),
    url(r'^$', views.player, name="home"),
    url(r'^play$', views.player, {'autoplay': True}, name="autoplay"),
    url(r'^get_artist_donate_address$', views.get_artist_donate_address, name="get_artist_donate_address"),
    url(r'^upload$', views.upload, name="upload"),
    url(r'^stats$', views.station_stats, name='station_stats'),
]

if settings.DEBUG:
    urlpatterns.append(
        url(r'^mp3/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    )
