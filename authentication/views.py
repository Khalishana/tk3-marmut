import psycopg2
from django.shortcuts import render, redirect
from django.http import HttpResponse
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
        password = (request.POST['password'])
        name = request.POST['name']
        gender = request.POST['gender']
        birth_place = request.POST['birth_place']
        birth_date = request.POST['birth_date']
        hometown = request.POST['hometown']
        role_podcaster = 'role_podcaster' in request.POST
        role_artist = 'role_artist' in request.POST
        role_songwriter = 'role_songwriter' in request.POST

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
            return HttpResponse("Email already registered as user or label")
            # return render(request, 'login.html', {
            #     'error_message': "Email already registered as user or label",
            #     'show_form': 'userForm'
            # })
        
        print(password)

        # Masukkan data ke tabel akun
        cur.execute("""
            INSERT INTO marmut.akun (email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, password, name, gender, birth_place, birth_date, is_verified, hometown))

        # Secara otomatis menetapkan Pengguna memiliki akun Non-Premium
        cur.execute("""
            INSERT INTO marmut.nonpremium (email)
            VALUES (%s)
        """, (email,))

        conn.commit()
        cur.close()
        conn.close()

        return HttpResponse("User registered successfully")
        # return render(request, 'login.html', {
        #     'success_message': "User registered successfully",
        #     'show_form': 'userForm'
        # })
    
    return render(request, 'login.html', {'show_form': 'registerOptions'})

def register_label(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = (request.POST['password'])
        name = request.POST['name']
        contact = request.POST['contact']
        id_pemilik_hak_cipta = "default_id"  # Atur default atau nilai sebenarnya jika ada

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
        
        # Masukkan data ke tabel label
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
        cur.close()
        conn.close()
        if user is None:
            return HttpResponse("Invalid login credentials")
        if user[0] == password:
            return redirect('authentication:show_landing')
        else:
            return HttpResponse("Invalid login credentials")

    return render(request, 'login.html')

def show_landing(request):
    return render(request, 'landing_page.html', {'user': request.user})

def logout_view(request):
    # tambahkan logika logout sesuai kebutuhan
    return redirect('authentication:login')