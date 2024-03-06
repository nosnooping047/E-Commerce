from django.contrib import admin
from .models import Categoria, Subcategoria1, Subcategoria2, Subcategoria3, Produto
# Register your models here.

class ProdutoAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'descricao', 'marca']  # Adicione os campos que deseja pesquisar

admin.site.register(Produto, ProdutoAdmin)

class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ['nome']  # Adicione os campos que deseja pesquisar

admin.site.register(Categoria, CategoriaAdmin)

admin.site.register(Subcategoria1)
admin.site.register(Subcategoria2)
admin.site.register(Subcategoria3)