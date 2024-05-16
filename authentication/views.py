import random
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
        cur.execute("SELECT COUNT(*) FROM marmut.akun WHERE email = %s", (email,))
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM marmut.label WHERE email = %s", (email,))
        label_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM marmut.nonpremium WHERE email = %s", (email,))
        nonpremium_count = cur.fetchone()[0]

        if user_count > 0 or label_count > 0 or nonpremium_count > 0:
            return HttpResponse("Email sudah terdaftar sebagai pengguna atau label")

        # Masukkan data ke tabel akun
        cur.execute("""
            INSERT INTO marmut.akun (email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, password, name, gender, birth_place, birth_date, is_verified, hometown))

        # Tambahkan ke tabel role jika role dipilih
        if role_podcaster:
            cur.execute("INSERT INTO marmut.podcaster (email) VALUES (%s)", (email,))
        if role_artist:
            cur.execute("INSERT INTO marmut.pemilik_hak_cipta (id, rate_royalti) VALUES (%s, %s) ", (id_pemilik_hak_cipta, rate_royalti))
            cur.execute("INSERT INTO marmut.artist (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)", (uuid.uuid4(), email, id_pemilik_hak_cipta))
            
        if role_songwriter:
            cur.execute("""
            INSERT INTO marmut.pemilik_hak_cipta (id, rate_royalti)
            VALUES (%s, %s)
        """, (id_pemilik_hak_cipta, rate_royalti))
            cur.execute("INSERT INTO marmut.songwriter (id, email_akun, id_pemilik_hak_cipta) VALUES (%s, %s, %s)", (uuid.uuid4(), email, id_pemilik_hak_cipta))

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
        cur.execute("SELECT COUNT(*) FROM marmut.akun WHERE email = %s", (email,))
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM marmut.label WHERE email = %s", (email,))
        label_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM marmut.nonpremium WHERE email = %s", (email,))
        nonpremium_count = cur.fetchone()[0]

        if user_count > 0 or label_count > 0 or nonpremium_count > 0:
            return HttpResponse("Email already registered as user or label")
            # return render(request, 'login.html', {
            #     'error_message': "Email already registered as user or label",
            #     'show_form': 'labelForm'
            # })

        # Masukkin data ke tabel label
        cur.execute("""
            INSERT INTO marmut.pemilik_hak_cipta (id, rate_royalti)
            VALUES (%s, %s)
        """, (id_pemilik_hak_cipta, rate_royalti))
        cur.execute("""
            INSERT INTO marmut.label (id, nama, email, password, kontak, id_pemilik_hak_cipta)
            VALUES (%s, %s, %s, %s, %s)
        """, (uuid.uuid4(), name, email, password, contact, id_pemilik_hak_cipta))
        
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
        
        cur.execute("SELECT password FROM marmut.akun WHERE email = %s", (username,))
        user = cur.fetchone()
        
        if user is None:
            cur.execute("SELECT password FROM marmut.label WHERE email = %s", (username,))
            label = cur.fetchone()
            
            if label is None:
                cur.close()
                conn.close()
                return HttpResponse("Invalid login credentials")
            else:
                response = redirect('authentication:show_landing')
                response.set_cookie('email', username) 
                return response
            
        
        if user[0] == password:
            response = redirect('authentication:show_landing')
            user_roles = []

            # Check roles
            cur.execute("SELECT COUNT(*) FROM marmut.songwriter WHERE email_akun = %s", (username,))
            if cur.fetchone()[0] > 0:
                user_roles.append('songwriter')

            cur.execute("SELECT COUNT(*) FROM marmut.artist WHERE email_akun = %s", (username,))
            if cur.fetchone()[0] > 0:
                user_roles.append('artist')

            cur.execute("SELECT COUNT(*) FROM marmut.podcaster WHERE email = %s", (username,))
            if cur.fetchone()[0] > 0:
                user_roles.append('podcaster')

            # Set cookies for roles
            response.set_cookie('user_id', str(uuid.uuid4()), max_age=365*24*60*60)  # 1 year
            response.set_cookie('user_roles', ','.join(user_roles), max_age=365*24*60*60)  # 1 year
            response.set_cookie('email', username) 
            
            cur.close()
            conn.close()
            return response
        else:
            cur.close()
            conn.close()
            return HttpResponse("Invalid login credentials")
        
        

    return render(request, 'login.html')

def show_landing(request):
    user_id = request.COOKIES.get('user_id')
    return render(request, 'landing_page.html', {'user_id': user_id})

def logout_view(request):
    response = HttpResponseRedirect(reverse('authentication:login'))
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response