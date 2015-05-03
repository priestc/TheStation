import urllib2

from django import forms
from .models import Song, Artist
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

class NewSongForm(forms.ModelForm):
    artist = forms.CharField(widget=forms.TextInput)
    image_url = forms.URLField(required=False)

    def clean_artist(self):
        artist, c = Artist.objects.get_or_create(name=self.cleaned_data['artist'])
        return artist

    def save(self, *args, **kwargs):
        url = self.cleaned_data['image_url']
        if not self.cleaned_data['image'] and url:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(url).read())
            img_temp.flush()
            self.cleaned_data['image'] = File(img_temp)

        return super(NewSongForm, self).save(*args, **kwargs)

    class Meta:
        model = Song
        exclude = ('featuring', )
        widgets = {
            'collection': forms.TextInput,
            'genre': forms.TextInput,
            'subgenre': forms.TextInput,
            'title': forms.TextInput,
        }
