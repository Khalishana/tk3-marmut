from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse

from django.urls import reverse
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

# views.py

def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            return None


def create_podcast(request):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        genre = request.POST.getlist('genre')
        tanggal_rilis = request.POST.get('tanggal_rilis')
        tahun = request.POST.get('tahun')
        durasi = request.POST.get('durasi')

        email = request.COOKIES.get('email')

        # Insert into KONTEN table first
        konten_query = "INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi) VALUES (gen_random_uuid(), %s, %s, %s, %s) RETURNING id"
        konten_result = execute_query(konten_query, [judul, tanggal_rilis, tahun, durasi])
        id_konten = konten_result[0]['id']

        # Insert into PODCAST table using the id from KONTEN
        podcast_query = "INSERT INTO PODCAST (id_konten, email_podcaster) VALUES (%s, %s)"
        execute_query(podcast_query, [id_konten, email])

        # Insert genres into GENRE table
        for g in genre:
            execute_query("INSERT INTO GENRE (id_konten, genre) VALUES (%s, %s)", [id_konten, g])
        
        return redirect('kelola_podcast:list_podcast')
    return render(request, 'create_podcast.html')

def list_podcast(request):
    query = """
        SELECT p.id_konten, k.judul, COUNT(e.id_episode) AS jumlah_episode, COALESCE(SUM(e.durasi), 0) AS total_durasi
        FROM PODCAST p
        LEFT JOIN EPISODE e ON p.id_konten = e.id_konten_podcast
        LEFT JOIN KONTEN k ON p.id_konten = k.id
        WHERE p.email_podcaster = %s
        GROUP BY p.id_konten, k.judul
    """
    email = request.COOKIES.get('email')
    podcasts = execute_query(query, [email])
    return render(request, 'list_podcast.html', {'podcasts': podcasts})

def delete_podcast(request, id_konten):
    execute_query("DELETE FROM PODCAST WHERE id_konten = %s", [id_konten])
    return redirect('kelola_podcast:list_podcast')

def add_episode(request, id_konten):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        durasi = request.POST.get('durasi')
        query = "INSERT INTO EPISODE (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis) VALUES (gen_random_uuid(), %s, %s, %s, %s, CURRENT_DATE)"
        execute_query(query, [id_konten, judul, deskripsi, durasi])
        return redirect('kelola_podcast:list_episodes', id_konten=id_konten)
    return render(request, 'add_episode.html', {'id_konten': id_konten})

def list_episodes(request, id_konten):
    query = "SELECT * FROM EPISODE WHERE id_konten_podcast = %s"
    episodes = execute_query(query, [id_konten])
    return render(request, 'list_episodes.html', {'episodes': episodes, 'id_konten': id_konten})

def delete_episode(request, id_episode, id_konten):
    execute_query("DELETE FROM EPISODE WHERE id_episode = %s", [id_episode])
    return redirect('kelola_podcast:list_episodes', id_konten=id_konten)