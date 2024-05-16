from django.shortcuts import render
from django.db import connection

# Create your views here.
def show_langganan(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }
    return render(request, "langganan.html", context)

def show_pembayaran(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }
    return render(request, "pembayaran.html", context)

def show_riwayat(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }
    return render(request, "riwayat.html", context)

def show_transactions(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO marmut;")
        cursor.execute("""
            SELECT jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal 
            FROM transaction
        """)
        transactions = cursor.fetchall()

    print(transactions)

    context = {
        'transactions': transactions
    }
    return render(request, 'riwayat.html', context)

def show_paket_langganan(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO marmut;")
        cursor.execute("""
            SELECT jenis, harga
            FROM paket
        """)
        pakets = cursor.fetchall()

    context = {
        'pakets': pakets
    }
    return render(request, 'langganan.html', context)