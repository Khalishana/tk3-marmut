from django.shortcuts import render
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

def show_album(request):
    email = request.COOKIES.get('email')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM marmut.label\
                WHERE email = %s", (email,))
    label = cur.fetchmany()
    
    # Mengecek apakah merupakan label
    if len(label) == 1:
        id_label = label[0][0]
        
        cur.execute("SELECT * FROM marmut.album\
                    WHERE id_label = %s", (id_label,))
        showed_album = cur.fetchall()
        
        context = {
            'role': 'label',
            'status': 'success',
            'nama': label[0][1],
            'showed_album': showed_album,
        }
        
        response = render(request, 'list_album.html', context)
        response.set_cookie('role', 'label')
        response.set_cookie('email', email)
        response.set_cookie('id', label[0][0])
        response.set_cookie('idPemilikCiptaLabel', label[0][5])
        
        conn.commit()
        cur.close()
        conn.close()
        
        return response
    
    return render(request, 'list_album.html')

def show_song(request):
    album_id = request.GET.get('album_id')
    showed_song = []
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT nama FROM marmut.album \
                WHERE id = %s", (album_id,))
    album_name = cur.fetchone()[0]
    
    cur.execute("SELECT id_konten, total_play, total_download FROM marmut.song \
                WHERE id_album = %s", (album_id,))
    showed_song = cur.fetchall()
    
    for i in range(len(showed_song)):
        cur.execute("SELECT judul, tanggal_rilis, tahun, durasi FROM marmut.konten \
                    WHERE id = %s", (showed_song[i][0],))
        showed_song[i] = showed_song[i] + cur.fetchone()

    context = {
        'status': 'success',
        'showed_song': showed_song,
        'album_name': album_name, 
    }
    
    response = render(request, 'song_album.html', context)
    conn.commit()
    cur.close()
    conn.close()
    return response

def delete_album(request):
    album_id = request.GET.get('album_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM marmut.album WHERE id = %s", (album_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return render(request, 'list_album.html')

def delete_song(request):
    song_id = request.GET.get('song_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM marmut.song WHERE id_konten = %s", (song_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return render(request, 'song_album.html')
