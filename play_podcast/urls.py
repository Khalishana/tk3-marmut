# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('podcast/<uuid:id_konten>/', views.podcast_detail, name='podcast_detail'),
]
