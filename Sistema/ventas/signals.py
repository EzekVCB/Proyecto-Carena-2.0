from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Venta, Compra, DetalleVenta, DetalleCompra, Producto, TransaccionInventario, Inventario
from django.db.models import F
from django.utils import timezone
from decimal import Decimal
from django.db import transaction

@receiver(post_save, sender=Producto)
def crear_inventario(sender, instance, created, **kwargs):
    """
    Crea automáticamente un registro de inventario cuando se crea un nuevo producto
    """
    if created:
        Inventario.objects.create(
            producto=instance,
            stock_actual=0,
            stock_minimo=0
        )

@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_venta(sender, instance, created, **kwargs):
    """
    Actualiza el stock cuando se realiza una venta
    """
    if created:
        with transaction.atomic():
            inventario = instance.Producto.inventario
            stock_anterior = inventario.stock_actual
            nuevo_stock = stock_anterior - instance.Cantidad
            
            if nuevo_stock < 0:
                raise ValueError('No hay suficiente stock para realizar esta venta')
            
            # Registrar la transacción
            TransaccionInventario.objects.create(
                inventario=inventario,
                tipo_movimiento='SAL',
                origen_movimiento='VEN',
                cantidad=instance.Cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=nuevo_stock,
                documento_referencia=f'Venta #{instance.Venta.id}',
                usuario='Sistema'
            )
            
            # Actualizar el stock
            inventario.stock_actual = nuevo_stock
            inventario.save()

@receiver(post_save, sender=DetalleCompra)
def actualizar_stock_compra(sender, instance, created, **kwargs):
    """
    Actualiza el stock cuando se realiza una compra
    """
    if created:
        with transaction.atomic():
            inventario = instance.Producto.inventario
            stock_anterior = inventario.stock_actual
            nuevo_stock = stock_anterior + instance.Cantidad
            
            # Registrar la transacción
            TransaccionInventario.objects.create(
                inventario=inventario,
                tipo_movimiento='ENT',
                origen_movimiento='COM',
                cantidad=instance.Cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=nuevo_stock,
                documento_referencia=f'Compra #{instance.Compra.id}',
                usuario='Sistema'
            )
            
            # Actualizar el stock
            inventario.stock_actual = nuevo_stock
            inventario.save()

@receiver(pre_save, sender=TransaccionInventario)
def validar_stock_negativo(sender, instance, **kwargs):
    """
    Valida que el stock no quede negativo después de una transacción
    """
    if instance.tipo_movimiento in ['SAL', 'MER']:
        stock_final = instance.inventario.stock_actual - instance.cantidad
        if stock_final < 0:
            raise ValueError('No hay suficiente stock para realizar esta operación') 