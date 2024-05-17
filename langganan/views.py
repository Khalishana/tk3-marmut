import uuid
from django.shortcuts import redirect, render
from django.db import connection
from django.contrib import messages

def get_current_user_email(request):
    return request.COOKIES.get('email')

# Create your views here.
def show_langganan(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO marmut;")
        cursor.execute("SELECT jenis, harga FROM paket")
        pakets = cursor.fetchall()
    
    context = {
        'pakets': pakets
    }
    return render(request, "langganan.html", context)

def show_pembayaran(request):
    if request.method == 'POST':
        jenis_paket = request.POST.get('jenis_paket')
        harga_paket = request.POST.get('harga_paket')

        context = {
            'jenis_paket': jenis_paket,
            'harga_paket': harga_paket
        }
        return render(request, "pembayaran.html", context)
    else:
        return redirect('langganan:show_langganan')

def show_riwayat(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }
    return render(request, "riwayat.html", context)

def show_transactions(request):
    email = get_current_user_email(request)
    if not email:
        messages.error(request, "You need to be logged in to view transactions.")
        return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("SELECT jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal FROM transaction WHERE email = %s", [email])
        transactions = cursor.fetchall()

    context = {
        'transactions': transactions
    }
    return render(request, 'riwayat.html', context)

def show_paket_langganan(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT jenis, harga
            FROM paket
        """)
        pakets = cursor.fetchall()

    context = {
        'pakets': pakets
    }
    return render(request, 'langganan.html', context)

def purchase_subscription(request):
    if request.method == 'POST':
        email = request.COOKIES.get('email')
        if not email:
            messages.error(request, "Anda harus login terlebih dahulu untuk berlangganan")
            return redirect('authentication:login')

        jenis_paket = request.POST.get('jenis_paket')
        harga_paket = request.POST.get('harga_paket')
        metode_bayar = request.POST.get('metode_bayar')

        with connection.cursor() as cursor:
            # cek apakah ada langganan yang masih aktif
            cursor.execute("""
                SELECT COUNT(*) 
                FROM transaction 
                WHERE email = %s AND timestamp_berakhir > NOW()
            """, [email])
            active_subscription_count = cursor.fetchone()[0]

            if active_subscription_count > 0:
                messages.error(request, "Anda sudah memiliki langganan yang aktif.")
                context = {
                    'jenis_paket': jenis_paket,
                    'harga_paket': harga_paket
                }
                return render(request, 'pembayaran.html', context)

            # masukkan transaksi baru
            cursor.execute("""
                INSERT INTO transaction (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal)
                VALUES (%s, %s, %s, NOW(), NOW() + INTERVAL '1 month', %s, %s)
            """, (str(uuid.uuid4()), jenis_paket, email, metode_bayar, harga_paket))

            # menambahkan pengguna ke tabel premium
            cursor.execute("""
                INSERT INTO premium (email)
                VALUES (%s)
                ON CONFLICT (email) DO NOTHING
            """, [email])

            messages.success(request, "Langganan berhasil dibeli!")
            return redirect('langganan:show_transactions')

    return redirect('langganan:show_paket_langganan')