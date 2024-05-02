from django.shortcuts import render

# Create your views here.

def create_episode(request):
    return render(request, "create_episode.html")

def create_podcast(request):
    return render(request, "create_podcast.html")

def daftar_episode(request):
    return render(request, "daftar_episode.html")

def list_podcast(request):
    return render(request, "list_podcast.html")