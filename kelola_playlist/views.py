import datetime
import random
import psycopg2
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import uuid

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
        SELECT id_user_playlist, judul, deskripsi, jumlah_lagu, total_durasi, id_playlist
        FROM user_playlist
        WHERE email_pembuat = %s
    """, (email,))
    playlists = cur.fetchall()
    cur.close()
    conn.close()

    playlists_data = []
    for playlist in playlists:
        playlists_data.append({
            'id_user_playlist': playlist[0],
            'judul': playlist[1],
            'jumlah_lagu': playlist[3],
            'total_durasi_jam': playlist[4]//60,
            'total_durasi_menit': playlist[4]%60,
            'id': playlist[5]
        })

    context = {
        'playlists': playlists_data
    }

    return render(request, 'manage_playlists.html', context)

def add_playlist(request):
    if request.method == 'POST':
        email = request.COOKIES.get('email')

        if not email:
            return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']
        id_user_playlist = str(uuid.uuid4())
        id_playlist = str(uuid.uuid4())
        tanggal_dibuat = timezone.now().date()

        conn = get_db_connection()
        cur = conn.cursor()
        
        # Masukkan entri baru ke tabel PLAYLIST
        cur.execute("""
            INSERT INTO playlist (id)
            VALUES (%s)
        """, (id_playlist,))
        
        # Masukkan data ke tabel USER_PLAYLIST
        cur.execute("""
            INSERT INTO user_playlist (email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, id_user_playlist, judul, deskripsi, 0, tanggal_dibuat, id_playlist, 0))
        conn.commit()
        cur.close()
        conn.close()

        return redirect('kelola_playlist:manage_playlists')

    return render(request, 'add_playlist.html')

def playlist_detail(request, id):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ambil detail playlist
    cur.execute("""
        SELECT p.id_user_playlist, p.judul, p.deskripsi, p.jumlah_lagu, p.total_durasi, p.tanggal_dibuat, a.nama, p.id_playlist
        FROM user_playlist p
        JOIN akun a ON p.email_pembuat = a.email
        WHERE p.id_playlist = %s AND p.email_pembuat = %s
    """, (id, email))
    playlist = cur.fetchone()
    
    if not playlist:
        cur.close()
        conn.close()
        return HttpResponse("Playlist tidak ditemukan", status=404)
    
    playlist_data = {
        'id_user_playlist': playlist[0],
        'judul': playlist[1],
        'deskripsi': playlist[2],
        'jumlah_lagu': playlist[3],
        'total_durasi_jam': playlist[4]//60,
        'total_durasi_menit': playlist[4]%60,
        'tanggal_dibuat': playlist[5],
        'pembuat': playlist[6],
        'id': playlist[7],
        'lagu': []
    }
    
    # Ambil daftar lagu dalam playlist
    cur.execute("""
        SELECT k.judul, k.durasi, k.id, string_agg(ak.nama, ', ') as artist_names
        FROM playlist_song ps
        JOIN konten k ON ps.id_song = k.id
        JOIN songwriter_write_song sws ON k.id = sws.id_song
        JOIN songwriter sw ON sws.id_songwriter = sw.id
        JOIN akun ak ON sw.email_akun = ak.email
        WHERE ps.id_playlist = %s
        GROUP BY k.judul, k.durasi, k.id
    """, (id,))
    songs = cur.fetchall()
    
    for song in songs:
        playlist_data['lagu'].append({
            'judul': song[0],
            'durasi': song[1],
            'artist': song[3],
            'id': song[2]
        })
    
    cur.close()
    conn.close()
    
    context = {
        'playlist': playlist_data
    }

    return render(request, 'playlist_detail.html', context)

def shuffle_play(request, id):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Cari id_user_playlist dengan menggunakan id_playlist dan email
        cur.execute("""
            SELECT id_user_playlist
            FROM user_playlist
            WHERE id_playlist = %s AND email_pembuat = %s
        """, (id, email))
        result = cur.fetchone()

        if not result:
            cur.close()
            conn.close()
            return HttpResponse("Playlist tidak ditemukan atau bukan milik Anda", status=404)

        id_user_playlist = result[0]
        timestamp = datetime.datetime.now()

        # Insert entry to AKUN_PLAY_USER_PLAYLIST
        cur.execute("""
            INSERT INTO akun_play_user_playlist (email_pemain, id_user_playlist, email_pembuat, waktu)
            VALUES (%s, %s, %s, %s)
        """, (email, id_user_playlist, email, timestamp))

        # Get songs in the playlist
        cur.execute("""
            SELECT id_song
            FROM playlist_song
            WHERE id_playlist = %s
        """, (id,))
        song_ids = cur.fetchall()

        # Shuffle song_ids
        song_ids = [song[0] for song in song_ids]
        random.shuffle(song_ids)

        # Insert entries to AKUN_PLAY_SONG
        for song_id in song_ids:
            cur.execute("""
                INSERT INTO akun_play_song (email_pemain, id_song, waktu)
                VALUES (%s, %s, %s)
            """, (email, song_id, timestamp))

        conn.commit()
        cur.close()
        conn.close()

        return redirect('kelola_playlist:playlist_detail', id=id)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)

def add_song(request, idPlaylist):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ambil daftar lagu yang tersedia
    cur.execute("""
        SELECT k.id, k.judul, string_agg(ak.nama, ', ') as artist_names
        FROM konten k
        JOIN songwriter_write_song sws ON k.id = sws.id_song
        JOIN songwriter sw ON sws.id_songwriter = sw.id
        JOIN akun ak ON sw.email_akun = ak.email
        GROUP BY k.id, k.judul
    """)
    available_songs = cur.fetchall()

    songs_data = []
    for song in available_songs:
        songs_data.append({
            'id': song[0],
            'title': song[1],
            'artist': song[2]
        })

    cur.close()
    conn.close()
    
    context = {
        'playlist_id': idPlaylist,
        'available_songs': songs_data
    }
    
    return render(request, 'add_song.html', context)

def add_song_to_playlist(request, idPlaylist):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    song_id = request.POST['lagu']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Cek apakah lagu sudah ada di playlist
        cur.execute("""
            SELECT COUNT(*)
            FROM playlist_song
            WHERE id_playlist = %s AND id_song = %s
        """, (idPlaylist, song_id))
        result = cur.fetchone()

        if result[0] > 0:
            cur.close()
            conn.close()
            return HttpResponse("Lagu sudah ada di playlist", status=400)

        # Tambahkan lagu ke playlist
        cur.execute("""
            INSERT INTO playlist_song (id_playlist, id_song)
            VALUES (%s, %s)
        """, (idPlaylist, song_id))
        
        # Perbarui jumlah lagu dan total durasi di user_playlist
        cur.execute("""
            UPDATE user_playlist
            SET jumlah_lagu = jumlah_lagu + 1,
                total_durasi = total_durasi + (SELECT durasi FROM konten WHERE id = %s)
            WHERE id_playlist = %s
        """, (song_id, idPlaylist))

        conn.commit()
        cur.close()
        conn.close()

        return redirect('kelola_playlist:playlist_detail', id=idPlaylist)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)

def update_playlist(request, idPlaylist):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT judul, deskripsi
        FROM user_playlist
        WHERE id_playlist = %s AND email_pembuat = %s
    """, (idPlaylist, email))
    playlist = cur.fetchone()

    if not playlist:
        cur.close()
        conn.close()
        return HttpResponse("Playlist tidak ditemukan atau bukan milik Anda", status=404)

    context = {
        'playlist_id': idPlaylist,
        'judul': playlist[0],
        'deskripsi': playlist[1]
    }

    cur.close()
    conn.close()

    return render(request, 'update_playlist.html', context)

def save_updated_playlist(request, idPlaylist):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    judul = request.POST['judul']
    deskripsi = request.POST['deskripsi']

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE user_playlist
            SET judul = %s, deskripsi = %s
            WHERE id_playlist = %s AND email_pembuat = %s
        """, (judul, deskripsi, idPlaylist, email))

        conn.commit()
        cur.close()
        conn.close()

        return redirect('kelola_playlist:manage_playlists')
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)

def delete_playlist(request, idPlaylist):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Cek apakah playlist kosong
        cur.execute("""
            SELECT COUNT(*)
            FROM playlist_song
            WHERE id_playlist = %s
        """, (idPlaylist,))
        count = cur.fetchone()[0]

        if count > 0:
            # Hapus lagu-lagu dari playlist_song jika playlist tidak kosong
            cur.execute("""
                DELETE FROM playlist_song
                WHERE id_playlist = %s
            """, (idPlaylist,))

        # Hapus playlist dari user_playlist
        cur.execute("""
            DELETE FROM user_playlist
            WHERE id_playlist = %s AND email_pembuat = %s
        """, (idPlaylist, email))

        # Hapus entri dari tabel PLAYLIST
        cur.execute("""
            DELETE FROM playlist
            WHERE id = %s
        """, (idPlaylist,))

        conn.commit()
        cur.close()
        conn.close()

        return redirect('kelola_playlist:manage_playlists')
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)


def song_detail(request, idPlaylist, idSong):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    # Ambil detail lagu
    cur.execute("""
        SELECT k.judul, k.durasi, k.tanggal_rilis, k.tahun, COALESCE(s.total_play, 0) as total_play, 
               COALESCE(s.total_download, 0) as total_download, a.nama as artist_name, al.judul as album_name
        FROM konten k
        LEFT JOIN song s ON k.id = s.id_konten
        LEFT JOIN album al ON s.id_album = al.id
        LEFT JOIN artist ar ON s.id_artist = ar.id
        LEFT JOIN akun a ON ar.email_akun = a.email
        WHERE k.id = %s
    """, (idSong,))
    song = cur.fetchone()

    if not song:
        cur.close()
        conn.close()
        return HttpResponse("Lagu tidak ditemukan", status=404)

    # Ambil genre lagu
    cur.execute("""
        SELECT g.genre
        FROM genre g
        WHERE g.id_konten = %s
    """, (idSong,))
    genres = cur.fetchall()

    # Ambil songwriters
    cur.execute("""
        SELECT a.nama
        FROM songwriter_write_song sws
        JOIN songwriter sw ON sws.id_songwriter = sw.id
        JOIN akun a ON sw.email_akun = a.email
        WHERE sws.id_song = %s
    """, (idSong,))
    songwriters = cur.fetchall()

    cur.close()
    conn.close()

    context = {
        'song': {
            'judul': song[0],
            'durasi': song[1],
            'tanggal_rilis': song[2],
            'tahun': song[3],
            'total_play': song[4],
            'total_download': song[5],
            'artist': song[6],
            'album': song[7],
            'id': idSong
        },
        'genres': [genre[0] for genre in genres],
        'songwriters': [songwriter[0] for songwriter in songwriters],
        'idPlaylist': idPlaylist
    }

    return render(request, 'play_song.html', context)

def play_song(request, idSong):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        timestamp = datetime.datetime.now()

        # Masukkan entri baru ke tabel AKUN_PLAY_SONG
        cur.execute("""
            INSERT INTO akun_play_song (email_pemain, id_song, waktu)
            VALUES (%s, %s, %s)
        """, (email, idSong, timestamp))
        
        # Update total play di tabel SONG
        cur.execute("""
            UPDATE song
            SET total_play = total_play + 1
            WHERE id_konten = %s
        """, (idSong,))

        conn.commit()
        cur.close()
        conn.close()

        return HttpResponse("""
            <script>
                alert('Lagu berhasil dimainkan!');
                window.location.href = document.referrer;
            </script>
        """)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)
    
def delete_song(request, idPlaylist, idSong):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Hapus lagu dari playlist
        cur.execute("""
            DELETE FROM playlist_song
            WHERE id_playlist = %s AND id_song = %s
        """, (idPlaylist, idSong))

        conn.commit()
        cur.close()
        conn.close()

        return HttpResponse("""
            <script>
                alert('Lagu berhasil dihapus dari playlist!');
                window.location.href = document.referrer;
            </script>
        """)
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)

def play_song_detail(request, idSong):
    if request.method == 'POST':
        email = request.COOKIES.get('email')

        if not email:
            return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

        progress = int(request.POST.get('progress', 0))

        if progress <= 70:
            return redirect('kelola_playlist:song_detail', idSong=idSong)

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            timestamp = datetime.datetime.now()

            # Masukkan entri baru ke tabel AKUN_PLAY_SONG
            cur.execute("""
                INSERT INTO akun_play_song (email_pemain, id_song, waktu)
                VALUES (%s, %s, %s)
            """, (email, idSong, timestamp))

            # Update total play di tabel SONG
            cur.execute("""
                UPDATE song
                SET total_play = total_play + 1
                WHERE id_konten = %s
            """, (idSong,))

            conn.commit()
            cur.close()
            conn.close()

            return HttpResponse("""
                <script>
                    alert('Lagu berhasil dimainkan!');
                    window.location.href = document.referrer;
                </script>
            """)
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return HttpResponse(f"Terjadi kesalahan: {str(e)}", status=500)
    else:
        return HttpResponse("Metode request tidak diizinkan", status=405)

def add_to_playlist(request, idSong):
    email = request.COOKIES.get('email')

    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    if request.method == 'GET':
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Dapatkan daftar playlist pengguna
        cur.execute("""
            SELECT id_user_playlist, judul
            FROM user_playlist
            WHERE email_pembuat = %s
        """, (email,))
        playlists = cur.fetchall()
        
        # Dapatkan detail lagu
        cur.execute("""
            SELECT k.judul, ak.nama
            FROM konten k
            JOIN song s ON k.id = s.id_konten
            JOIN artist ar ON s.id_artist = ar.id
            JOIN akun ak ON ar.email_akun = ak.email
            WHERE k.id = %s
        """, (idSong,))
        song = cur.fetchone()
        
        cur.close()
        conn.close()

        context = {
            'playlists': playlists,
            'song': {
                'id': idSong,
                'judul': song[0],
                'artist': song[1]
            }
        }

        return render(request, 'add_to_playlist.html', context)

    elif request.method == 'POST':
        id_user_playlist = request.POST.get('playlist')

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # Dapatkan id_playlist sebenarnya
            cur.execute("""
                SELECT id_playlist
                FROM user_playlist
                WHERE id_user_playlist = %s
            """, (id_user_playlist,))
            id_playlist = cur.fetchone()[0]

            # Cek apakah lagu sudah ada di playlist
            cur.execute("""
                SELECT COUNT(*)
                FROM playlist_song
                WHERE id_playlist = %s AND id_song = %s
            """, (id_playlist, idSong))
            count = cur.fetchone()[0]

            if count > 0:
                cur.close()
                conn.close()
                return render(request, 'kelola_playlist/add_to_playlist_result.html', {
                    'message': f"Lagu dengan judul '{song[0]}' sudah ditambahkan di playlist ini!",
                    'song_id': idSong,
                    'playlist_id': id_playlist
                })

            # Tambahkan lagu ke playlist
            cur.execute("""
                INSERT INTO playlist_song (id_playlist, id_song)
                VALUES (%s, %s)
            """, (id_playlist, idSong))

            # Update jumlah lagu dan total durasi di user_playlist
            cur.execute("""
                UPDATE user_playlist
                SET jumlah_lagu = jumlah_lagu + 1,
                    total_durasi = total_durasi + (SELECT durasi FROM konten WHERE id = %s)
                WHERE id_user_playlist = %s
            """, (idSong, id_playlist))

            conn.commit()
            cur.close()
            conn.close()

            return render(request, 'kelola_playlist/add_to_playlist_result.html', {
                'message': f"Berhasil menambahkan Lagu dengan judul '{song[0]}' ke playlist ini!",
                'song_id': idSong,
                'playlist_id': id_playlist
            })
        except Exception as e:
            
            return HttpResponse(f"Berhasil memasukkan playlist", status=500)
    else:
        return HttpResponse("Metode request tidak diizinkan", status=405)