from django.shortcuts import render
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres.vjxypfaouaiqkavqanuu",
        password="marmutkelompok9",
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        port="5432",
    )
    return conn

# Create your views here.
def show_royalti(request):
    role = request.COOKIES.get('user_roles')
    email = request.COOKIES.get('email')
    royalti = []
    
    if isinstance(role, str):
        role = role.split(',')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if "label" in role:
        cur.execute("SELECT id_pemilik_hak_cipta FROM label \
                    WHERE email = %s", (email,))
        hak_cipta_label = cur.fetchone()[0]
        
        cur.execute("SELECT rate_royalti FROM pemilik_hak_cipta \
                    WHERE id = %s", (hak_cipta_label,))
        update_royalti = cur.fetchone()[0]
    
        cur.execute("SELECT id_song, jumlah FROM royalti \
                    WHERE id_pemilik_hak_cipta = %s", (hak_cipta_label,))
        royalti = cur.fetchall()
        
        if len(royalti) != 0:
            for i in range(len(royalti)):
                cur.execute("SELECT id_album, total_play, total_download FROM song \
                            WHERE id_konten = %s", (royalti[i][0],))
                song_info = cur.fetchone()
                total_royalti = update_royalti * song_info[1]  
                cur.execute("UPDATE royalti SET jumlah = %s WHERE id_song = %s AND id_pemilik_hak_cipta = %s", (total_royalti, royalti[i][0], hak_cipta_label))
                cur.execute("SELECT judul FROM album \
                            WHERE id = %s", (song_info[0],))
                album_title = cur.fetchone()
                cur.execute("SELECT judul FROM konten \
                            WHERE id = %s", (royalti[i][0],))
                title = cur.fetchone()
                title = list(title)
                title[0] = title[0].split('-')[0].strip()
                
                royalti[i] = royalti[i] + song_info + album_title + tuple(title)
    else:
        if "songwriter" in role:
            cur.execute("SELECT id_pemilik_hak_cipta FROM songwriter \
                        WHERE email_akun = %s", (email,))
            hak_cipta_songwriter = cur.fetchone()[0]
            
            cur.execute("SELECT rate_royalti FROM pemilik_hak_cipta \
                        WHERE id = %s", (hak_cipta_songwriter,))
            update_royalti = cur.fetchone()[0]
            
            cur.execute("SELECT id_song, jumlah FROM royalti \
                        WHERE id_pemilik_hak_cipta = %s", (hak_cipta_songwriter,))
            royalti = cur.fetchall()
            
            if len(royalti) != 0:
                for i in range(len(royalti)):
                    cur.execute("SELECT id_album, total_play, total_download FROM song \
                                WHERE id_konten = %s", (royalti[i][0],))
                    song_info = cur.fetchone()
                    total_royalti = update_royalti * song_info[1]  
                    cur.execute("UPDATE royalti SET jumlah = %s WHERE id_song = %s AND id_pemilik_hak_cipta = %s", (total_royalti, royalti[i][0], hak_cipta_songwriter))
                    cur.execute("SELECT judul FROM album \
                                WHERE id = %s", (song_info[0],))
                    album_title = cur.fetchone()
                    cur.execute("SELECT judul FROM konten \
                                WHERE id = %s", (royalti[i][0],))
                    title = cur.fetchone()
                    title = list(title)
                    title[0] = title[0].split('-')[0].strip()
                    
                    royalti[i] = royalti[i] + song_info + album_title + tuple(title)

        if "artist" in role:
            cur.execute("SELECT id_pemilik_hak_cipta FROM artist \
                        WHERE email_akun = %s", (email,))
            hak_cipta_artist = cur.fetchone()[0]
            
            cur.execute("SELECT rate_royalti FROM pemilik_hak_cipta \
                        WHERE id = %s", (hak_cipta_artist,))
            update_royalti = cur.fetchone()[0]
            
            cur.execute("SELECT id_song, jumlah FROM royalti \
                        WHERE id_pemilik_hak_cipta = %s", (hak_cipta_artist,))
            royalti_artist = cur.fetchall()
            
            if len(royalti_artist) != 0:
                for i in range(len(royalti_artist)):
                    cur.execute("SELECT id_album, total_play, total_download FROM song \
                                WHERE id_konten = %s", (royalti_artist[i][0],))
                    song_info = cur.fetchone()
                    total_royalti = update_royalti * song_info[1]  
                    cur.execute("UPDATE royalti SET jumlah = %s WHERE id_song = %s AND id_pemilik_hak_cipta = %s", (total_royalti, royalti_artist[i][0], hak_cipta_artist))
                    cur.execute("SELECT judul FROM album \
                                WHERE id = %s", (song_info[0],))
                    album_title = cur.fetchone()
                    cur.execute("SELECT judul FROM konten \
                                WHERE id = %s", (royalti_artist[i][0],))
                    title = cur.fetchone()
                    title = list(title)
                    title[0] = title[0].split('-')[0].strip()
                    
                    royalti_artist[i] = royalti_artist[i] + song_info + album_title + tuple(title)
                    
            royalti += royalti_artist

    context = {
        'status': 'success',
        'role': role,
        'royalti': royalti,
    }
    
    conn.commit()
    cur.close()
    conn.close()
    return render(request, 'royalti.html', context)