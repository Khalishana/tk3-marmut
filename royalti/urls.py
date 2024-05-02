from django.urls import path
from royalti.views import show_royalti

app_name = 'royalti'

urlpatterns = [
    path('', show_royalti, name='show_royalti'),
]