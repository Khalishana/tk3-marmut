from django.urls import path
from play_podcast.views import play_podcast

app_name = 'play_podcast'

urlpatterns = [
    path('play_podcast/', play_podcast, name='play_podcast'),
]