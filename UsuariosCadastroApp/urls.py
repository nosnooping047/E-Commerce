from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"),
    path('logar/', views.logar, name="login"),
    path('logout/', views.logout, name="logout"),
    path('minha_conta/', views.minha_conta, name='minha_conta'),
    path('buscar_endereco/', views.buscar_endereco, name='buscar_endereco'),

]