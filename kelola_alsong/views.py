from django.shortcuts import render

# Create your views here.

def show_create_album(request):
    return render(request, "create_album.html")

def show_create_song(request):
    return render(request, "create_song.html")

def show_kelola_album(request):
    return render(request, "kelola_album.html")

def show_kelola_song(request):
    return render(request, "kelola_song.html")