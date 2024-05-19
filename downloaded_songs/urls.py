from django.urls import path
from downloaded_songs.views import search_bar, confirm_download, show_downloaded_songs, delete_downloaded_song

app_name = 'downloaded_songs'

urlpatterns = [
    path('', show_downloaded_songs, name='show_downloaded_songs'),
    path('search/', search_bar, name="search_bar"),
    path('confirm_download/<uuid:song_id>/', confirm_download, name='confirm_download'),
    path('delete_downloaded_song/<uuid:song_id>/', delete_downloaded_song, name='delete_downloaded_song'),
]