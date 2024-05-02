from django.urls import path
from .views import show_main

app_name = 'kelola_playlist'

urlpatterns = [
    path('', show_main, name='manage_playlists'),
]
