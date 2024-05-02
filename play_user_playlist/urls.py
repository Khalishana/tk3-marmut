from django.urls import path
from .views import show_main

app_name = 'play_user_playlist'

urlpatterns = [
    path('', show_main, name='play_user_playlist'),
]
