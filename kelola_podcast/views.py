from django.shortcuts import render

# Create your views here.

def show_create_episode(request):
    return render(request, "create_episode.html")

def show_create_podcast(request):
    return render(request, "create_podcast.html")

def show_daftar_episode(request):
    return render(request, "daftar_episode.html")

def show_list_podcast(request):
    return render(request, "list_podcast.html")