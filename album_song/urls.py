from django.urls import path
from album_song.views import show_album, show_song

app_name = 'royalti'

urlpatterns = [
    path('', show_album, name='show_album'),
    path('song', show_song, name='show_song'),
]