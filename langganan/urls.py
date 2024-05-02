from django.urls import path
from langganan.views import show_langganan, show_pembayaran, show_riwayat

app_name = 'langganan'

urlpatterns = [
    path('', show_langganan, name='show_langganan'),
    path('pembayaran/', show_pembayaran, name='show_pembayaran'),
    path('riwayat/', show_riwayat, name='show_riwayat'),
]
