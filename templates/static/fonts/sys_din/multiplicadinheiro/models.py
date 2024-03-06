from django.db import models

# Create your models here.

class InserirNew(models.Model):
    dadosnome = models.CharField(max_length=100)
    dadosvalor = models.CharField(max_length=100)