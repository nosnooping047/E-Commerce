# Generated by Django 5.0.2 on 2024-02-13 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InserirNew',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dadosnome', models.CharField(max_length=100)),
                ('dadosvalor', models.CharField(max_length=100)),
            ],
        ),
    ]