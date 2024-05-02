from django.urls import path
from downloaded_songs.views import show_download_page, search_bar

app_name = 'downloaded_songs'

urlpatterns = [
    path('', show_download_page, name='show_download_page'),
    path('search/', search_bar, name="search_bar")
]