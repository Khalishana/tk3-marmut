# urls.py

from django.urls import path
from . import views

app_name = 'melihat_chart'

urlpatterns = [
    path('charts/', views.chart_list, name='chart_list'),
    path('charts/<str:tipe>/', views.chart_detail, name='chart_detail'),
    path('song/<uuid:id_konten>/', views.song_detail, name='song_detail'),
]
