# Generated by Django 5.0.2 on 2024-02-14 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProdutosApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='imagem',
            field=models.ImageField(default='templates/static/upload/img/default.png', upload_to='templates/static/upload/img', verbose_name='Imagem'),
        ),
    ]