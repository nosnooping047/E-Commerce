from django.urls import path
from . import views

urlpatterns = [
    path('multiplicadinheiro/', views.multiplicadinheiro, name="multiplicadinheiro"),
    path('inserir/', views.inserir, name="inserir"),
]