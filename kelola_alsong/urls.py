from django.urls import path
from kelola_alsong.views import show_create_album, show_create_song, show_kelola_album, show_kelola_song

app_name = 'kelola_alsong'

urlpatterns = [
    path('create/album', show_create_album, name='show_create_album'),
    path('create/song', show_create_song, name='show_create_song'),
    path('album', show_kelola_album, name='show_kelola_album'),
    path('song', show_kelola_song, name='show_kelola_song'),
]