from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    ultimo_nome = models.CharField(max_length=100)  
    cpf = models.CharField(max_length=100)  
    telefone = models.CharField(max_length=20, blank=True)
    cep = models.CharField(max_length=10)
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=99)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

