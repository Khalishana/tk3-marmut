from django.db import models
from django.contrib.auth.models import User

class Playlist(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def duration(self):
        return sum(song.duration for song in self.songs.all())

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    duration = models.IntegerField()  # Durasi dalam menit
    playlist = models.ForeignKey(Playlist, related_name='songs', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} by {self.artist}"
