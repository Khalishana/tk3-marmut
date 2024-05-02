from django.shortcuts import render

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