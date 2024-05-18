import random
from django.db import connection
import psycopg2
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

def register_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        gender = request.POST['gender']
        birth_place = request.POST['birth_place']
        birth_date = request.POST['birth_date']
        hometown = request.POST['hometown']
        role_podcaster = 'role_podcaster' in request.POST
        role_artist = 'role_artist' in request.POST
        role_songwriter = 'role_songwriter' in request.POST
        id_pemilik_hak_cipta = str(uuid.uuid4())
        rate_royalti = random.randint(4,9)
        id_register = str(uuid.uuid4())

        user_roles = []
        if role_podcaster:
            user_roles.append('podcaster')
        if role_artist:
            user_roles.append('artist')
        if role_songwriter:
            user_roles.append('songwriter')

        # Tentukan status verifikasi berdasarkan role yang dipilih
        is_verified = role_podcaster or role_artist or role_songwriter

        conn = get_db_connection()
        cur = conn.cursor()

        # Cek apakah email sudah terdaftar di tabel akun, label, atau nonpremium
        cur.execute("SELECT COUNT(*) FROM akun WHERE email = %s", (email,))
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM label WHERE email = %s", (email,))
        label_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM nonpremium WHERE email = %s", (email,))
        nonpremium_count = cur.fetchone()[0]

        if user_count > 0 or label_count > 0 or nonpremium_count > 0:
            return HttpResponse("Email sudah terdaftar sebagai pengguna atau label")

        # Masukkan data ke tabel akun
        cur.execute("""
            INSERT INTO akun (email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, password, name, gender, birth_place, birth_date, is_verified, hometown))

        # Tambahkan ke tabel role jika role dipilih
        if role_podcaster:
            cur.execute("INSERT INTO marmut.podcaster (email) VALUES (%s)", (email,))
        if role_artist or role_songwriter:
            cur.execute("INSERT INTO marmut.pemilik_hak_cipta (id, rate_royalti) VALUES (%s, %s) ", (id_pemilik_hak_cipta, rate_royalti))
            if role_artist:
                cur.execute("INSERT INTO marmut.artist (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)", (id_register, email, id_pemilik_hak_cipta))
            if role_songwriter:
                cur.execute("INSERT INTO marmut.songwriter (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)", (id_register, email, id_pemilik_hak_cipta))

        conn.commit()
        cur.close()
        conn.close()

        response = HttpResponse("User registered successfully")
        return response
    
    return render(request, 'login.html', {'show_form': 'registerOptions'})

def register_label(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = (request.POST['password'])
        name = request.POST['name']
        contact = request.POST['contact']
        id_pemilik_hak_cipta = str(uuid.uuid4())
        rate_royalti = random.randint(4,9)

        conn = get_db_connection()
        cur = conn.cursor()

        # Cek apakah email sudah terdaftar di tabel akun, label, atau nonpremium
        cur.execute("SELECT COUNT(*) FROM akun WHERE email = %s", (email,))
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM label WHERE email = %s", (email,))
        label_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM nonpremium WHERE email = %s", (email,))
        nonpremium_count = cur.fetchone()[0]

        if user_count > 0 or label_count > 0 or nonpremium_count > 0:
            return HttpResponse("Email already registered as user or label")
            # return render(request, 'login.html', {
            #     'error_message': "Email already registered as user or label",
            #     'show_form': 'labelForm'
            # })

        # Masukkin data ke tabel label
        cur.execute("INSERT INTO pemilik_hak_cipta (id, rate_royalti) VALUES (%s, %s)", (id_pemilik_hak_cipta, rate_royalti))
        cur.execute("INSERT INTO label (id, nama, email, password, kontak, id_pemilik_hak_cipta) VALUES (%s, %s, %s, %s, %s, %s)", (str(uuid.uuid4()), name, email, password, contact, id_pemilik_hak_cipta))
        
        conn.commit()
        cur.close()
        conn.close()

        return HttpResponse("Label registered successfully")
        # return render(request, 'login.html', {
        #     'success_message': "Label registered successfully",
        #     'show_form': 'labelForm'
        # })

    return render(request, 'login.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT password FROM akun WHERE email = %s", (username,))
        user = cur.fetchone()
        
        if user is None:
            cur.execute("SELECT password FROM label WHERE email = %s", (username,))
            label = cur.fetchone()
            
            if label is None or label[0] != password:
                cur.close()
                conn.close()
                return HttpResponse("Invalid login credentials")
            else:
                response = redirect('authentication:show_landing')
                user_roles = ['label']  
                response.set_cookie('email', username)
                response.set_cookie('user_id', str(uuid.uuid4()), max_age=365*24*60*60)  # 1 year
                response.set_cookie('user_roles', ','.join(user_roles), max_age=365*24*60*60)  # 1 year
                cur.close()
                conn.close()
                return response
            
        
        if user[0] == password:
            response = redirect('authentication:show_landing')
            user_roles = []

            # Check roles
            cur.execute("SELECT COUNT(*) FROM songwriter WHERE email_akun = %s", (username,))
            if cur.fetchone()[0] > 0:
                user_roles.append('songwriter')

            cur.execute("SELECT COUNT(*) FROM artist WHERE email_akun = %s", (username,))
            if cur.fetchone()[0] > 0:
                user_roles.append('artist')

            cur.execute("SELECT COUNT(*) FROM podcaster WHERE email = %s", (username,))
            if cur.fetchone()[0] > 0:
                user_roles.append('podcaster')

            if not user_roles:  
                user_roles.append('regular_user')

            # Check premium status
            cur.execute("SELECT COUNT(*) FROM premium WHERE email = %s", (username,))
            is_premium = cur.fetchone()[0] > 0

            print(f"is_premium: {is_premium}")

            # Set cookies for roles and premium status
            response.set_cookie('user_id', str(uuid.uuid4()), max_age=365*24*60*60)  # 1 year
            response.set_cookie('user_roles', ','.join(user_roles), max_age=365*24*60*60)  # 1 year
            response.set_cookie('email', username)
            response.set_cookie('is_premium', str(is_premium).lower(), max_age=365*24*60*60)  # 1 year
            
            cur.close()
            conn.close()
            return response
        else:
            cur.close()
            conn.close()
            return HttpResponse("Invalid login credentials")

    return render(request, 'login.html')

def show_landing(request):
    email = request.COOKIES.get('email')
    if not email:
        return HttpResponse("Email tidak ditemukan dalam cookies", status=400)

    user_data = {}
    is_label = False

    with connection.cursor() as cursor:
        # Mengecek apakah email terdaftar sebagai label
        cursor.execute("SELECT nama, email, kontak FROM label WHERE email = %s", [email])
        result = cursor.fetchone()
        if result:
            user_data['nama'] = result[0]
            user_data['email'] = result[1]
            user_data['kontak'] = result[2]
            is_label = True
        else:
            # Mengambil data dari tabel akun
            cursor.execute("""
                SELECT nama, email, kota_asal, gender, tempat_lahir, tanggal_lahir 
                FROM akun 
                WHERE email = %s
            """, [email])
            result = cursor.fetchone()
            if result:
                user_data['nama'] = result[0]
                user_data['email'] = result[1]
                user_data['kota_asal'] = result[2]
                user_data['gender'] = 'Perempuan' if result[3] == 0 else 'Laki-laki'
                user_data['tempat_lahir'] = result[4]
                user_data['tanggal_lahir'] = result[5]

            # Mengecek role pengguna
            roles = []
            cursor.execute("SELECT 1 FROM songwriter WHERE email_akun = %s", [email])
            if cursor.fetchone():
                roles.append('Songwriter')

            cursor.execute("SELECT 1 FROM artist WHERE email_akun = %s", [email])
            if cursor.fetchone():
                roles.append('Artist')

            cursor.execute("SELECT 1 FROM podcaster WHERE email = %s", [email])
            if cursor.fetchone():
                roles.append('Podcaster')

            if not roles:
                roles.append('Pengguna Biasa')

            user_data['role'] = ', '.join(roles)

            # Mengecek status langganan
            cursor.execute("SELECT 1 FROM premium WHERE email = %s", [email])
            if cursor.fetchone():
                user_data['status_langganan'] = 'Premium'
            else:
                cursor.execute("SELECT 1 FROM nonpremium WHERE email = %s", [email])
                if cursor.fetchone():
                    user_data['status_langganan'] = 'Nonpremium'
                else:
                    user_data['status_langganan'] = 'Tidak diketahui'

            # Mengambil data playlist jika pengguna biasa
            if 'Pengguna Biasa' in roles:
                cursor.execute("""
                    SELECT judul
                    FROM user_playlist
                    WHERE email_pembuat = %s
                """, [email])
                playlists = cursor.fetchall()
                if playlists:
                    user_data['playlists'] = [playlist[0] for playlist in playlists]
                else:
                    user_data['playlists'] = None

    user_data['is_label'] = is_label
    return render(request, 'landing_page.html', user_data)

def logout_view(request):
    response = HttpResponseRedirect(reverse('authentication:login'))
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response