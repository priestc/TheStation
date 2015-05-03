import urllib2

from django import forms
from .models import Song, Artist
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

class SongFormImageURL(forms.ModelForm):
    image_url = forms.URLField(required=False)

    def clean(self, *args, **kwargs):
        all_data = self.cleaned_data
        url = all_data['image_url']
        image = all_data['image']

        if not image and url:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(url).read())
            img_temp.flush()
            all_data['image'] = File(img_temp)

        return all_data

    class Meta:
        model = Song
        exclude = ('featuring', )
        widgets = {
            'collection': forms.TextInput,
            'genre': forms.TextInput,
            'subgenre': forms.TextInput,
            'title': forms.TextInput,
        }

class UploadSongForm(SongFormImageURL):
    artist = forms.CharField(widget=forms.TextInput)

    def clean_artist(self):
        artist, c = Artist.objects.get_or_create(name=self.cleaned_data['artist'])
        return artist
