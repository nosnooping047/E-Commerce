from django.urls import path
from . import views  # Certifique-se de que o nome do módulo esteja correto e que o arquivo views.py exista no mesmo diretório


urlpatterns = [
    path('home/', views.home, name="home"),
]