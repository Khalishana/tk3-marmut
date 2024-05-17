from django.shortcuts import render
from django.db import connection

# Create your views here.
def show_download_page(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }
    return render(request, "download.html", context)

def search_bar(request):
    query = request.GET.get('query', '').lower()  # Get the query and convert it to lowercase
    results = []
    message = ""

    if query:
        with connection.cursor() as cursor:
            # Searching in Podcasts
            cursor.execute("""
                SELECT 'PODCAST' AS type,
                k.judul AS judul,
                a.nama AS oleh
                FROM podcast p
                JOIN konten k ON p.id_konten = k.id
                JOIN podcaster pod ON p.email_podcaster = pod.email
                JOIN akun a ON pod.email = a.email
                WHERE LOWER(k.judul) LIKE %s
            """, [f"%{query}%"])
            podcast_results = cursor.fetchall()
            results.extend(podcast_results)

            # Debugging: Print hasil query podcast
            print("Podcast Results:", podcast_results)

            # Searching in Songs
            cursor.execute("""
                SELECT 'SONG' AS type,
                k.judul AS judul,
                a.nama AS oleh
                FROM song s
                JOIN konten k ON s.id_konten = k.id
                JOIN artist ar ON s.id_artist = ar.id
                JOIN akun a ON ar.email_akun = a.email
                WHERE LOWER(k.judul) LIKE %s OR LOWER(a.nama) LIKE %s
            """, [f"%{query}%", f"%{query}%"])
            song_results = cursor.fetchall()
            results.extend(song_results)
            print("Song Results:", song_results)

            # Searching in User Playlists
            cursor.execute("""
                SELECT 'USER PLAYLIST' AS type,
                up.judul AS judul,
                a.nama AS oleh
                FROM user_playlist up
                JOIN akun a ON up.email_pembuat = a.email
                WHERE LOWER(up.judul) LIKE %s
            """, [f"%{query}%"])
            playlist_results = cursor.fetchall()
            results.extend(playlist_results)
            print("Playlist Results:", playlist_results)

    if not results:
        message = f"Maaf, pencarian untuk '{query}' tidak ditemukan."

    context = {
        'query': query,
        'results': [{
            'type': result[0],
            'title': result[1],
            'by': result[2],
            'url': '#'  # Placeholder for the URL. Update this as needed.
        } for result in results],
        'message': message
    }
    return render(request, 'search_bar.html', context)