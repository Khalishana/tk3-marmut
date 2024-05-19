import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
import psycopg2

from kelola_playlist.views import get_db_connection

# Create your views here.
def show_downloaded_songs(request):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    # Ambil daftar lagu yang diunduh oleh pengguna saat ini
    cur.execute("""
        SELECT DISTINCT k.id, k.judul, ak.nama, up.id_playlist
        FROM downloaded_song ds
        JOIN konten k ON ds.id_song = k.id
        JOIN songwriter_write_song sws ON k.id = sws.id_song
        JOIN songwriter sw ON sws.id_songwriter = sw.id
        JOIN akun ak ON sw.email_akun = ak.email
        LEFT JOIN user_playlist up ON k.id = up.id_playlist
        WHERE ds.email_downloader = %s
    """, (email,))
    songs = cur.fetchall()

    cur.close()
    conn.close()

    songs_data = []
    current_date = datetime.date.today().strftime("%d/%m/%Y")
    for song in songs:
        songs_data.append({
            'id': song[0],
            'judul': song[1],
            'oleh': song[2],
            'id_playlist': song[0],
            'tanggal_download': current_date
        })

    context = {
        'songs': songs_data
    }

    return render(request, 'download.html', context)

def search_bar(request):
    query = request.GET.get('query', '').lower()  
    results = {}
    message = ""

    if query:
        with connection.cursor() as cursor:
            # Searching in Podcasts
            cursor.execute("""
                SELECT 'PODCAST' AS type, k.judul AS judul, COALESCE(a.nama, 'Unknown') AS oleh, k.id
                FROM konten k
                LEFT JOIN podcast p ON k.id = p.id_konten
                LEFT JOIN podcaster pod ON p.email_podcaster = pod.email
                LEFT JOIN akun a ON pod.email = a.email
                WHERE LOWER(k.judul) LIKE %s
            """, [f"%{query}%"])
            podcast_results = cursor.fetchall()
            for result in podcast_results:
                results[result[1].lower()] = {
                    'type': result[0],
                    'title': result[1],
                    'by': result[2],
                    'id': result[3],
                    'url': f"/play_podcast/podcast/{result[3]}",
                    'id_playlist': None  
                }

            # Searching in Songs
            cursor.execute("""
                SELECT 'SONG' AS type, k.judul AS judul, COALESCE(a.nama, 'Unknown') AS oleh, k.id
                FROM song s
                JOIN konten k ON s.id_konten = k.id
                JOIN artist ar ON s.id_artist = ar.id
                JOIN akun a ON ar.email_akun = a.email
                WHERE LOWER(k.judul) LIKE %s OR LOWER(a.nama) LIKE %s
            """, [f"%{query}%", f"%{query}%"])
            song_results = cursor.fetchall()
            for result in song_results:
                results[result[1].lower()] = {
                    'type': result[0],
                    'title': result[1],
                    'by': result[2],
                    'id': result[3],
                    'id_playlist': None  
                }

            print("Song Results:", song_results)

            # Searching in User Playlists
            cursor.execute("""
                SELECT 'USER PLAYLIST' AS type, up.judul AS judul, COALESCE(a.nama, 'Unknown') AS oleh, up.id_playlist
                FROM user_playlist up
                JOIN akun a ON up.email_pembuat = a.email
                WHERE LOWER(up.judul) LIKE %s
            """, [f"%{query}%"])
            playlist_results = cursor.fetchall()
            for result in playlist_results:
                if result[1].lower() not in results:
                    results[result[1].lower()] = {
                        'type': result[0],
                        'title': result[1],
                        'by': result[2],
                        'id': result[3],
                        'id_playlist': result[3]  
                    }

            print("Playlist Results:", playlist_results)

    if not results:
        message = f"Maaf, pencarian untuk '{query}' tidak ditemukan."

    context = {
        'query': query,
        'results': list(results.values()),
        'message': message
    }
    return render(request, 'search_bar.html', context)

def confirm_download(request, song_id):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Dapatkan judul lagu berdasarkan song_id
        cur.execute("SELECT judul FROM konten WHERE id = %s", (str(song_id),))
        result = cur.fetchone()
        if not result:
            return HttpResponse("Lagu tidak ditemukan", status=404)
        song_title = result[0]

        # Periksa apakah lagu sudah diunduh sebelumnya
        cur.execute("SELECT COUNT(*) FROM downloaded_song WHERE id_song = %s AND email_downloader = %s", (str(song_id), email))
        if cur.fetchone()[0] > 0:
            context = {
                'error_message': f"Lagu dengan judul '{song_title}' sudah pernah diunduh!"
            }
            return render(request, 'confirm_download.html', context)

        # Insert the download record into downloaded_song table
        cur.execute("""
            INSERT INTO downloaded_song (id_song, email_downloader)
            VALUES (%s, %s)
        """, (str(song_id), email))
        conn.commit()
        cur.close()
        conn.close()

        context = {
            'message': f"Berhasil mengunduh Lagu dengan judul '{song_title}'!"
        }
        return render(request, 'confirm_download.html', context)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)

def delete_downloaded_song(request, song_id):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Hapus lagu dari tabel downloaded_song
        cur.execute("DELETE FROM downloaded_song WHERE id_song = %s AND email_downloader = %s", (str(song_id), email))
        conn.commit()

        # Dapatkan judul lagu berdasarkan song_id
        cur.execute("SELECT judul FROM konten WHERE id = %s", (str(song_id),))
        result = cur.fetchone()
        if not result:
            return HttpResponse("Lagu tidak ditemukan", status=404)
        song_title = result[0]

        cur.close()
        conn.close()

        context = {
            'message': f"Berhasil menghapus Lagu dengan judul '{song_title}' dari daftar unduhan!"
        }
        return render(request, 'delete_confirmation.html', context)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)