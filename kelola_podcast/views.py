from django.shortcuts import render

import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres.vjxypfaouaiqkavqanuu",
        password="marmutkelompok9",
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        port="5432"
    )
    return conn

def create_episode(request):
    return render(request, "create_episode.html")

def create_podcast(request):
    return render(request, "create_podcast.html")

def daftar_episode(request):
    return render(request, "daftar_episode.html")

def list_podcast(request):
    return render(request, "list_podcast.html")