from django.shortcuts import render

# Create your views here.

def show_album(request):
    return render(request, "list_album.html")

def show_song(request):
    return render(request, "song_album.html")