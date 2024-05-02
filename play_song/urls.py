from django.urls import path
from .views import show_main

app_name = 'play_song'

urlpatterns = [
    path('', show_main, name='play_song'),
]
