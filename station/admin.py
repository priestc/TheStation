from django.contrib import admin

# Register your models here.

from .models import Artist, Song, StationPlay

def generate_address(modeladmin, request, queryset):
    for artist in queryset:
        if not artist.address:
            artist.generate_address()

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    actions = [generate_address]
    exclude = ('private_key_hex', )
    #readonly_fields = ('private_key_wif', )

admin.site.register(StationPlay)
admin.site.register(Song)
admin.site.register(Artist, ArtistAdmin)
