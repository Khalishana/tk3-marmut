from django.urls import path
from langganan.views import show_langganan, show_pembayaran, show_riwayat, show_transactions, show_paket_langganan

app_name = 'langganan'

urlpatterns = [
    #path('', show_langganan, name='show_langganan'),
    path('', show_paket_langganan, name='show_paket_langganan'),
    path('pembayaran/', show_pembayaran, name='show_pembayaran'),
    #path('riwayat/', show_riwayat, name='show_riwayat'),
    path('riwayat/', show_transactions, name='show_transactions'),
]
