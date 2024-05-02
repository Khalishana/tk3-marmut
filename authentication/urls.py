from django.urls import path, include
from authentication.views import register 
from authentication.views import login_user
from authentication.views import logout_user
from authentication.views import show_landing

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('', show_landing, name='show_landing'),
]