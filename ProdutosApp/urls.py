from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.produtos, name="produtos"),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('statusDePagamento/', views.statusDePagamento, name='statusDePagamento'),
    path('pagamento/', views.pagamento, name='pagamento'),
    path('calcular_frete_melhor_envio/',views.calcular_frete_melhor_envio, name='calcular_frete_melhor_envio'),
    path('processar_selecao_frete/', views.processar_selecao_frete, name='processar_selecao_frete'), 
]