import psycopg2
from django.shortcuts import render, redirect
from django.http import HttpResponse

def get_db_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres.vjxypfaouaiqkavqanuu",
        password="marmutkelompok9",
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        port="5432"
    )
    return conn

def show_main(request):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_user_playlist, judul, deskripsi, jumlah_lagu, total_durasi
        FROM user_playlist
        WHERE email_pembuat = %s
    """, (email,))
    playlists = cur.fetchall()
    cur.close()
    conn.close()

    # Mengubah hasil query menjadi daftar dictionary
    playlists_data = []
    for playlist in playlists:
        playlists_data.append({
            'id': playlist[0],
            'judul': playlist[1],
            'jumlah_lagu': playlist[3],
            'total_durasi': playlist[4]
        })

    context = {
        'playlists': playlists_data
    }

    return render(request, 'manage_playlists.html', context)
