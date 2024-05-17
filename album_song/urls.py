from django.urls import path
from album_song.views import show_album, show_song, delete_album, delete_song

app_name = 'album_song'

urlpatterns = [
    path('album', show_album, name='show_album'),
    path('song', show_song, name='show_song'),
    path('delete_song', delete_song, name='delete_song'),
    path('delete_album', delete_album, name='delete_album'),
]