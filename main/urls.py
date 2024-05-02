from django.urls import path
from main.views import show_main
from authentication.views import show_landing

app_name = 'main'

urlpatterns = [
    path('main/', show_main, name='show_main'),
    # path('', show_landing, name='show_landing'),
    #path('', include('authentication.urls'))
]