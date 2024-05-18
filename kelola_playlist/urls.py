from django.urls import path

from downloaded_songs.views import confirm_download
from .views import show_main, add_playlist, playlist_detail, shuffle_play, add_song, add_song_to_playlist, update_playlist, save_updated_playlist, delete_playlist, song_detail, play_song_detail, play_song, delete_song, add_to_playlist

app_name = 'kelola_playlist'

urlpatterns = [
    path('', show_main, name='manage_playlists'),
    path('add/', add_playlist, name='add_playlist'),
    path('detail/<uuid:id>/', playlist_detail, name='playlist_detail'),
    path('shuffle/<uuid:id>/', shuffle_play, name='shuffle_play'),
    path('add_song/<uuid:idPlaylist>/', add_song, name='add_song'),
    path('add_song_to_playlist/<uuid:idPlaylist>/', add_song_to_playlist, name='add_song_to_playlist'),
    path('update/<uuid:idPlaylist>/', update_playlist, name='update_playlist'),
    path('save_updated_playlist/<uuid:idPlaylist>/', save_updated_playlist, name='save_updated_playlist'),
    path('delete/<uuid:idPlaylist>/', delete_playlist, name='delete_playlist'),
    path('song_detail/<uuid:idPlaylist>/<uuid:idSong>/', song_detail, name='song_detail'),
    path('play_song_detail/<uuid:idSong>/', play_song_detail, name='play_song_detail'),
    path('play_song/<uuid:idSong>/', play_song, name='play_song'),
    path('delete_song/<uuid:idPlaylist>/<uuid:idSong>/', delete_song, name='delete_song'),
    path('add_to_playlist/<uuid:idSong>/', add_to_playlist, name='add_to_playlist'),
    path('download_song/<uuid:idSong>/', confirm_download, name='download_song'),
]
