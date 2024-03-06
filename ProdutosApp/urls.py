from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.produtos, name="produtos"),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('process_payment/', views.process_payment, name='process_payment'),
]