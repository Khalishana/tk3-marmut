from django.urls import path
from kelola_podcast.views import create_episode, create_podcast, daftar_episode, list_podcast

app_name = 'kelola_podcast'

urlpatterns = [
    path('create_episode/', create_episode, name='create_episode'),
    path('create_podcast/', create_podcast, name='create_podcast'),
    path('daftar_episode/', daftar_episode, name='daftar_episode'),
    path('list_podcast/', list_podcast, name='list_podcast'),
]