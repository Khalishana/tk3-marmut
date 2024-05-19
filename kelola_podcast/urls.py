from django.urls import path
from . import views

app_name = 'kelola_podcast'

urlpatterns = [
    path('create_podcast/', views.create_podcast, name='create_podcast'),
    path('list_podcast/', views.list_podcast, name='list_podcast'),
    path('delete_podcast/<uuid:id_konten>/', views.delete_podcast, name='delete_podcast'),
    path('add_episode/<uuid:id_konten>/', views.add_episode, name='add_episode'),
    path('list_episodes/<uuid:id_konten>/', views.list_episodes, name='list_episodes'),
    path('delete_episode/<uuid:id_episode>/<uuid:id_konten>/', views.delete_episode, name='delete_episode'),
]