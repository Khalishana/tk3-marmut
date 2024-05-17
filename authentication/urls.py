from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('', views.login, name='login'),
    path('register/user', views.register_user, name='register_user'),
    path('register/label', views.register_label, name='register_label'),
    path('dashboard/', views.show_landing, name='show_landing'),
    path('logout/', views.logout_view, name='logout'),
]
