# Generated by Django 5.1.3 on 2025-03-02 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0003_egreso_productosegreso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='Fecha',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
