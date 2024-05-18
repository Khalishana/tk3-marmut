import random
import psycopg2
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
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

def show_create_album(request):
    role = request.COOKIES.get('user_roles') 
    if isinstance(role, str):
        role = role.split(',')
        
    email = request.COOKIES.get('email')

    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        judul_album = request.POST.get('judul_album')
        label = request.POST.get('label')
        id_album = str(uuid.uuid4())
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("INSERT INTO album \
                    VALUES (%s, %s, 0, %s, 0)", (id_album, judul_album, label))
        conn.commit()
        
        # Create song dibawah ini
        id_song = str(uuid.uuid4())
        judul = request.POST.get('judul')
        songwriters = request.POST.getlist('songwriter[]')
        genres = request.POST.getlist('genre[]')
        durasi = request.POST.get('durasi')
        current_datetime = datetime.now()
        date_now = current_datetime.strftime('%Y-%m-%d')
        current_year = current_datetime.year
        year_now = '{:04d}'.format(current_year)
        
        if "artist" in role:
            cur.execute("SELECT id FROM artist \
                        WHERE email_akun = %s", (email,))
            id_artist = cur.fetchone()[0]

        else:
            cur.execute("SELECT id FROM songwriter \
                        WHERE email_akun = %s", (email,))
            id_songwriter = cur.fetchone()[0]
        
        # Insert tabel token
        cur.execute("INSERT INTO konten \
                    VALUES (%s, %s, %s, %s, %s)", (id_song, judul, date_now, year_now, durasi))
        
        # Insert tabel song
        cur.execute("INSERT INTO song \
                    VALUES (%s, %s, %s, 0, 0)", (id_song, id_artist, id_album,))
        
        # Insert tabel songwriter_write_song
        for songwriter in songwriters:
            cur.execute("SELECT id_pemilik_hak_cipta FROM songwriter \
                        WHERE id = %s", (songwriter,))
            hak_cipta_songwriter = cur.fetchone()

            cur.execute("INSERT INTO royalti \
                        VALUES (%s, %s, 0)", (hak_cipta_songwriter[0], id_song,))

            cur.execute("INSERT INTO songwriter_write_song \
                        VALUES (%s, %s)", (songwriter, id_song,))
        
        # Insert tabel genre
        for genre in genres:
            cur.execute("INSERT INTO genre \
                        VALUES (%s, %s)", (id_song, genre,))
        
        # Id untuk hak cipta dari artist
        if "artist" in role:
            cur.execute("SELECT id FROM artist \
                        WHERE email_akun = %s", (email,))
            user_id = cur.fetchone()[0]
            cur.execute("SELECT id_pemilik_hak_cipta FROM artist \
                        WHERE id = %s", (user_id,))
            hak_cipta_artist = cur.fetchone()
        else:
            cur.execute("SELECT id FROM songwriter \
                        WHERE email_akun = %s", (email,))
            user_id = cur.fetchone()[0]
            cur.execute("SELECT id_pemilik_hak_cipta FROM artist \
                        WHERE id = %s", (user_id,))
            hak_cipta_artist = cur.fetchone()
        
        # Insert tabel royalti untuk artist
        cur.execute("INSERT INTO royalti \
                    VALUES (%s, %s, 0)", (hak_cipta_artist[0], id_song,))
        
        # Insert tabel royalti untuk label
        cur.execute("SELECT id_label FROM album \
                    WHERE id = %s", (id_album,))
        label = cur.fetchone()
        cur.execute("SELECT id_pemilik_hak_cipta FROM label \
                    WHERE id = %s", (label[0],))
        hak_cipta_label = cur.fetchone()
        cur.execute("INSERT INTO royalti \
                    VALUES (%s, %s, 0)", (hak_cipta_label[0], id_song,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect('kelola_alsong:show_kelola_album')
        
    cur.execute("SELECT id, nama FROM label")
    list_label = cur.fetchall()
    
    # Pilihan genre
    cur.execute("SELECT DISTINCT genre FROM genre")
    genre = cur.fetchall()
    
    
    # Piihan artist
    cur.execute("SELECT id, email_akun, id_pemilik_hak_cipta FROM artist")
    list_artist = cur.fetchall()
    for i in range(len(list_artist)):
        cur.execute("SELECT nama FROM akun\
                    WHERE email = %s", (list_artist[i][1],))
        list_artist[i] = list_artist[i] + cur.fetchone()
    
    # Piihan songwriter
    cur.execute("SELECT id, email_akun, id_pemilik_hak_cipta FROM songwriter")
    list_songwriter = cur.fetchall()
    for i in range(len(list_songwriter)):
        cur.execute("SELECT nama FROM akun\
                    WHERE email = %s", (list_songwriter[i][1],))
        list_songwriter[i] = list_songwriter[i] + cur.fetchone()
        
    # Nama artist dan songwriter
    if "artist" in role:
        cur.execute("SELECT nama FROM akun \
                    WHERE email = %s", (email,))
        nama_artist = cur.fetchone()[0]
    
    if "songwriter" in role:
        cur.execute("SELECT nama FROM akun \
                    WHERE email = %s", (email,))
        nama_songwriter = cur.fetchone()[0]
    
    context = {
        'list_label': list_label,  
        'genre': genre,
        'nama_artist': nama_artist,
        'nama_songwriter': nama_songwriter,
        'list_artist': list_artist,
        'list_songwriter': list_songwriter,
        'role': role,
    }
    
    conn.commit()
    cur.close()
    conn.close()
    return render(request, "create_album.html", context)

def show_create_song(request):
    role = request.COOKIES.get('user_roles') 
    if isinstance(role, str):
        role = role.split(',')
        
    album_id = request.GET.get('album_id')
    email = request.COOKIES.get('email')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        id_song = str(uuid.uuid4())
        judul = request.POST.get('judul')
        songwriters = request.POST.getlist('songwriter[]')
        genres = request.POST.getlist('genre[]')
        durasi = request.POST.get('durasi')
        current_datetime = datetime.now()
        date_now = current_datetime.strftime('%Y-%m-%d')
        current_year = current_datetime.year
        year_now = '{:04d}'.format(current_year)

        conn = get_db_connection()
        cur = conn.cursor()
        
        if "artist" in role:
            cur.execute("SELECT id FROM artist \
                        WHERE email_akun = %s", (email,))
            id_artist = cur.fetchone()[0]

        else:
            cur.execute("SELECT id FROM songwriter \
                        WHERE email_akun = %s", (email,))
            id_songwriter = cur.fetchone()[0]
        
        # Insert tabel token
        cur.execute("INSERT INTO konten \
                    VALUES (%s, %s, %s, %s, %s)", (id_song, judul, date_now, year_now, durasi))
        
        # Insert tabel song
        cur.execute("INSERT INTO song \
                    VALUES (%s, %s, %s, 0, 0)", (id_song, id_artist, album_id,))
        
        # Insert tabel songwriter_write_song
        for songwriter in songwriters:
            cur.execute("SELECT id_pemilik_hak_cipta FROM songwriter \
                        WHERE id = %s", (songwriter,))
            hak_cipta_songwriter = cur.fetchone()

            cur.execute("INSERT INTO royalti \
                        VALUES (%s, %s, 0)", (hak_cipta_songwriter[0], id_song,))

            cur.execute("INSERT INTO songwriter_write_song \
                        VALUES (%s, %s)", (songwriter, id_song,))
        
        # Insert tabel genre
        for genre in genres:
            cur.execute("INSERT INTO genre \
                        VALUES (%s, %s)", (id_song, genre,))
        
        # Id untuk hak cipta dari artist
        if "artist" in role:
            cur.execute("SELECT id FROM artist \
                        WHERE email_akun = %s", (email,))
            user_id = cur.fetchone()[0]
            cur.execute("SELECT id_pemilik_hak_cipta FROM artist \
                        WHERE id = %s", (user_id,))
            hak_cipta_artist = cur.fetchone()
        else:
            cur.execute("SELECT id FROM songwriter \
                        WHERE email_akun = %s", (email,))
            user_id = cur.fetchone()[0]
            cur.execute("SELECT id_pemilik_hak_cipta FROM artist \
                        WHERE id = %s", (user_id,))
            hak_cipta_artist = cur.fetchone()
        
        # Insert tabel royalti untuk artist
        cur.execute("INSERT INTO royalti \
                    VALUES (%s, %s, 0)", (hak_cipta_artist[0], id_song,))
        
        # Insert tabel royalti untuk label
        cur.execute("SELECT id_label FROM album \
                    WHERE id = %s", (album_id,))
        label = cur.fetchone()
        cur.execute("SELECT id_pemilik_hak_cipta FROM label \
                    WHERE id = %s", (label[0],))
        hak_cipta_label = cur.fetchone()
        cur.execute("INSERT INTO royalti \
                    VALUES (%s, %s, 0)", (hak_cipta_label[0], id_song,))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect('kelola_alsong:show_kelola_song', album_id=album_id)

    
    # Pilihan genre
    cur.execute("SELECT DISTINCT genre FROM genre")
    genre = cur.fetchall()
    
    # Pilihan album
    cur.execute("SELECT judul FROM album \
                WHERE id = %s", (album_id,))
    album_name = cur.fetchone()
    
    # Piihan artist
    cur.execute("SELECT id, email_akun, id_pemilik_hak_cipta FROM artist")
    list_artist = cur.fetchall()
    for i in range(len(list_artist)):
        cur.execute("SELECT nama FROM akun\
                    WHERE email = %s", (list_artist[i][1],))
        list_artist[i] = list_artist[i] + cur.fetchone()
    
    # Piihan songwriter
    cur.execute("SELECT id, email_akun, id_pemilik_hak_cipta FROM songwriter")
    list_songwriter = cur.fetchall()
    for i in range(len(list_songwriter)):
        cur.execute("SELECT nama FROM akun\
                    WHERE email = %s", (list_songwriter[i][1],))
        list_songwriter[i] = list_songwriter[i] + cur.fetchone()
        
    # Nama artist dan songwriter
    if "artist" in role:
        cur.execute("SELECT nama FROM akun \
                    WHERE email = %s", (email,))
        nama_artist = cur.fetchone()[0]
    
    if "songwriter" in role:
        cur.execute("SELECT nama FROM akun \
                    WHERE email = %s", (email,))
        nama_songwriter = cur.fetchone()[0]

    context = {
        'genre': genre,
        'album_name': album_name,
        'nama_artist': nama_artist,
        'nama_songwriter': nama_songwriter,
        'list_artist': list_artist,
        'list_songwriter': list_songwriter,
        'role': role,
    }
    conn.commit()
    cur.close()
    conn.close()
        
    return render(request, "create_song.html", context)

def show_kelola_album(request):
    role = request.COOKIES.get('user_roles') 
    if isinstance(role, str):
        role = role.split(',')
    list_album = []
    email = request.COOKIES.get('email')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT nama FROM akun \
                WHERE email = %s", (email,))
    nama_user = cur.fetchone()[0]
    
    if "artist" in role:
        cur.execute("SELECT id FROM artist \
                    WHERE email_akun = %s", (email,))
        user_id = cur.fetchone()[0]
        cur.execute("SELECT DISTINCT id_album FROM song\
                    WHERE id_artist = %s", (user_id,))
        album_artist = cur.fetchall()
        print(album_artist)
        if len(album_artist) != 0:
            for album_id in album_artist:
                cur.execute("SELECT id, judul, id_label, jumlah_lagu, total_durasi FROM album \
                            WHERE id = %s", (album_id[0],))
                album = cur.fetchone()
                if album is not None:  
                    list_album.append(album)
            for i in range(len(list_album)):
                cur.execute("SELECT nama FROM label \
                            WHERE id = %s", (list_album[i][2],))
                list_album[i] = list_album[i] + cur.fetchone() 

    if "songwriter" in role:
        cur.execute("SELECT id FROM songwriter \
                    WHERE email_akun = %s", (email,))
        user_id = cur.fetchone()[0]
        cur.execute("SELECT id_song FROM songwriter_write_song \
                    WHERE id_songwriter = %s", (user_id,))
        album_songwriter = cur.fetchall()
        if len(album_songwriter) != 0:
            for album_id in album_songwriter:
                cur.execute("SELECT id, judul, id_label, jumlah_lagu, total_durasi FROM album \
                            WHERE id = %s", (album_id[0],))
                album = cur.fetchone()
                if album is not None:  
                    list_album.append(album)
            for i in range(len(list_album)):
                cur.execute("SELECT nama FROM label \
                            WHERE id = %s", (list_album[i][2],))
                list_album[i] = list_album[i] + cur.fetchone() 

    context = {
        'status': 'success',
        'list_album': list_album,
        'nama_user': nama_user,
    }
    conn.commit()
    cur.close()
    conn.close()
    return render(request, "kelola_album.html", context)

def show_kelola_song(request, album_id):
    showed_song = []
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT judul FROM album \
                WHERE id = %s", (album_id,))
    album_name = cur.fetchone()[0]
    
    cur.execute("SELECT id_konten, total_play, total_download FROM song \
                WHERE id_album = %s", (album_id,))
    showed_song = cur.fetchall()
    
    for i in range(len(showed_song)):
        cur.execute("SELECT judul, tanggal_rilis, tahun, durasi FROM konten \
                    WHERE id = %s", (showed_song[i][0],))
        song_details = cur.fetchone()
        song_details = list(song_details)
        song_details[0] = song_details[0].split('-')[0].strip()
        showed_song[i] = showed_song[i] + tuple(song_details)

    context = {
        'status': 'success',
        'showed_song': showed_song,
        'album_name': album_name, 
    }
    
    conn.commit()
    cur.close()
    conn.close()
    return render(request, 'kelola_song.html', context)

def delete_album(request):
    album_id = request.GET.get('album_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM album WHERE id = %s", (album_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect('kelola_alsong:show_kelola_album')

def delete_song(request):
    song_id = request.GET.get('song_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM konten WHERE id = %s", (song_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect('kelola_alsong:show_kelola_album')