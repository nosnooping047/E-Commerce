from django.db import models
from django.utils.translation import gettext_lazy as _

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name=_("Nome da Categoria"))

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")

class Subcategoria1(models.Model):
    nome1 = models.CharField(max_length=100)

    def __str__(self):
        return self.nome1

class Subcategoria2(models.Model):
    nome2 = models.CharField(max_length=100)

    def __str__(self):
        return self.nome2

class Subcategoria3(models.Model):
    nome3 = models.CharField(max_length=100)

    def __str__(self):
        return self.nome3

class Produto(models.Model):
    nome = models.CharField(max_length=255, verbose_name=_("Nome"))
    descricao = models.TextField(verbose_name=_("Descrição"))
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Valor Pago"))
    valor_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Valor de Venda"))
    desconto_venda = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=_("Desconto de Venda"))
    valor_antigo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("Valor Antigo"))
    imagem = models.ImageField(upload_to='templates/static/upload/img', default='templates/static/upload/img/default.png', verbose_name=_("Imagem"))
    categorias = models.ManyToManyField(Categoria, verbose_name=_("Categorias"))
    subcategoria1 = models.ManyToManyField(Subcategoria1, blank=True)
    subcategoria2 = models.ManyToManyField(Subcategoria2, blank=True)
    subcategoria3 = models.ManyToManyField(Subcategoria3, blank=True)

    # Novos campos adicionados
    marca = models.CharField(max_length=100, verbose_name=_("Marca"))
    modelo = models.CharField(max_length=100, verbose_name=_("Modelo"))
    disponivel = models.BooleanField(default=True, verbose_name=_("Disponível"))
    quantidade_disponivel = models.PositiveIntegerField(default=0, verbose_name=_("Quantidade Disponível"))
    data_lancamento = models.DateField(verbose_name=_("Data de Lançamento"))
    
    # Campos relacionados a comentários e avaliações
    comentarios = models.TextField(blank=True, verbose_name=_("Comentários"))
    avaliacao = models.FloatField(default=0.0, verbose_name=_("Avaliação"))
    num_avaliacoes = models.PositiveIntegerField(default=0, verbose_name=_("Número de Avaliações"))

    # Campos SEO adicionados
    meta_description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Descrição"))
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Palavras-chave"))

    def __str__(self):
        return self.nome
