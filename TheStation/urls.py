from django.conf.urls import patterns, include, url
from django.contrib import admin
from station import views
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TheStation.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^current_and_next_song', views.current_and_next_song),
    url(r'^$', views.player),
    url(r'^upload', views.upload),
    (r'^mp3/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
