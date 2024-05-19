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

def chart_list(request):
    query = "SELECT tipe FROM CHART"
    charts = execute_query(query)
    return render(request, 'chart_list.html', {'charts': charts})

def chart_detail(request, tipe): #A.nama previously
    query = """
        SELECT S.id_konten, K.judul, AK.nama AS artist, K.tanggal_rilis, S.total_play 
        FROM SONG S
        JOIN KONTEN K ON S.id_konten = K.id
        JOIN ARTIST A ON S.id_artist = A.id
        JOIN AKUN AK ON A.email_akun = AK.email
        WHERE S.total_play > 0
        ORDER BY S.total_play DESC
        LIMIT 20
    """
    songs = execute_query(query)
    return render(request, 'chart_detail.html', {'tipe': tipe, 'songs': songs})

def song_detail(request, id_konten):
    query = """
        SELECT K.judul, AK.nama AS artist, K.tanggal_rilis, S.total_play, S.total_download
        FROM SONG S
        JOIN KONTEN K ON S.id_konten = K.id
        JOIN ARTIST A ON S.id_artist = A.id
        JOIN AKUN AK ON A.email_akun = AK.email
        WHERE S.id_konten = %s
    """
    song = execute_query(query, [id_konten])[0]
    return render(request, 'song_detail.html', {'song': song})