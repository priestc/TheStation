from django import forms
from .models import Song, Artist

class NewSongForm(forms.ModelForm):
    artist = forms.CharField(widget=forms.TextInput)

    def clean_artist(self):
        artist, c = Artist.objects.get_or_create(name=self.cleaned_data['artist'])
        return artist

    class Meta:
        model = Song
        exclude = ('featuring', )
        widgets = {
            'collection': forms.TextInput,
            #'artist': forms.TextInput,
            'genre': forms.TextInput,
            'subgenre': forms.TextInput,
            'title': forms.TextInput,
        }
