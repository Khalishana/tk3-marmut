from django.urls import path
from kelola_podcast.views import show_create_episode, show_create_podcast, show_daftar_episode, show_list_podcast

app_name = 'kelola_podcast'

urlpatterns = [
    path('create_episode', show_create_episode, name='show_create_episode'),
    path('create_podcast', show_create_podcast, name='show_create_podcast'),
    path('daftar_episode', show_daftar_episode, name='show_daftar_episode'),
    path('list_podcast', show_list_podcast, name='show_list_podcast'),
]