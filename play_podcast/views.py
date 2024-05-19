from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
import psycopg2

# Create your views here.
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

def format_duration(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours > 0:
        return f"{hours} jam {remaining_minutes} menit"
    else:
        return f"{remaining_minutes} menit"

def podcast_detail(request, id_konten):
    podcast_query = """
        SELECT K.judul, K.tanggal_rilis, K.tahun, A.nama AS podcaster
        FROM PODCAST P
        JOIN KONTEN K ON P.id_konten = K.id
        JOIN AKUN A ON P.email_podcaster = A.email
        WHERE P.id_konten = %s
    """
    podcast = execute_query(podcast_query, [id_konten])[0]

    genre_query = """
        SELECT genre
        FROM GENRE
        WHERE id_konten = %s
    """
    genres = execute_query(genre_query, [id_konten])

    episode_query = """
        SELECT E.judul, E.deskripsi, E.durasi, E.tanggal_rilis
        FROM EPISODE E
        WHERE E.id_konten_podcast = %s
        ORDER BY E.tanggal_rilis
    """
    episodes = execute_query(episode_query, [id_konten])

    # Calculate the total duration of all episodes
    total_duration = sum(episode['durasi'] for episode in episodes)

    # Format duration for episodes
    for episode in episodes:
        episode['durasi'] = format_duration(episode['durasi'])

    podcast['durasi'] = format_duration(total_duration)

    return render(request, 'play_podcast.html', {
        'podcast': podcast,
        'genres': [genre['genre'] for genre in genres],
        'episodes': episodes
    })


