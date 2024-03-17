# Generated by Django 5.0.3 on 2024-03-20 19:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome da Categoria')),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Subcategoria1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome1', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Subcategoria2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome2', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Subcategoria3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome3', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome')),
                ('descricao', models.TextField(verbose_name='Descrição')),
                ('valor_pago', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor Pago')),
                ('valor_venda', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor de Venda')),
                ('desconto_venda', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Desconto de Venda')),
                ('valor_antigo', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Valor Antigo')),
                ('imagem', models.ImageField(default='templates/static/upload/img/default.png', upload_to='templates/static/upload/img', verbose_name='Imagem')),
                ('marca', models.CharField(max_length=100, verbose_name='Marca')),
                ('modelo', models.CharField(max_length=100, verbose_name='Modelo')),
                ('largura', models.CharField(max_length=100, verbose_name='largura')),
                ('altura', models.CharField(max_length=100, verbose_name='altura')),
                ('comprimento', models.CharField(max_length=100, verbose_name='comprimento')),
                ('peso', models.CharField(max_length=100, verbose_name='peso')),
                ('disponivel', models.BooleanField(default=True, verbose_name='Disponível')),
                ('quantidade_disponivel', models.PositiveIntegerField(default=0, verbose_name='Quantidade Disponível')),
                ('data_lancamento', models.DateField(verbose_name='Data de Lançamento')),
                ('comentarios', models.TextField(blank=True, verbose_name='Comentários')),
                ('avaliacao', models.FloatField(default=0.0, verbose_name='Avaliação')),
                ('num_avaliacoes', models.PositiveIntegerField(default=0, verbose_name='Número de Avaliações')),
                ('meta_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta Descrição')),
                ('meta_keywords', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta Palavras-chave')),
                ('categorias', models.ManyToManyField(to='ProdutosApp.categoria', verbose_name='Categorias')),
                ('subcategoria1', models.ManyToManyField(blank=True, to='ProdutosApp.subcategoria1')),
                ('subcategoria2', models.ManyToManyField(blank=True, to='ProdutosApp.subcategoria2')),
                ('subcategoria3', models.ManyToManyField(blank=True, to='ProdutosApp.subcategoria3')),
            ],
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(default=1, verbose_name='Quantidade')),
                ('valor_total', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor Total')),
                ('data_compra', models.DateTimeField(auto_now_add=True, verbose_name='Data da Compra')),
                ('status', models.CharField(max_length=100, verbose_name='Status')),
                ('frete', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Frete')),
                ('codigo_rastreio', models.CharField(blank=True, max_length=100, null=True, verbose_name='Código de Rastreio')),
                ('id_para_rastreio', models.CharField(max_length=100, verbose_name='Id')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ProdutosApp.produto', verbose_name='Produto')),
            ],
            options={
                'verbose_name': 'Compra',
                'verbose_name_plural': 'Compras',
            },
        ),
    ]
