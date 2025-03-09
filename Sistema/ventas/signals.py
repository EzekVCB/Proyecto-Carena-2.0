from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Venta, Compra, DetalleVenta, DetalleCompra, Producto, TransaccionInventario, Inventario
from django.db.models import F
from django.utils import timezone
from decimal import Decimal

@receiver(post_save, sender=Producto)
def crear_inventario(sender, instance, created, **kwargs):
    """
    Crea automáticamente un registro de inventario cuando se crea un nuevo producto
    """
    if created:
        Inventario.objects.create(
            producto=instance,
            stock_actual=instance.Cantidad or 0,
            stock_minimo=instance.CantidadMinimaSugerida or 0
        )

@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_venta(sender, instance, created, **kwargs):
    """
    Actualiza el stock cuando se realiza una venta
    """
    if created:  # Solo si es un nuevo detalle de venta
        producto = instance.Producto
        cantidad_vendida = instance.Cantidad
        inventario = producto.inventario

        # Registrar la transacción
        TransaccionInventario.objects.create(
            inventario=inventario,
            tipo_movimiento='SAL',
            origen_movimiento='VEN',
            cantidad=cantidad_vendida,
            stock_anterior=inventario.stock_actual,
            stock_nuevo=inventario.stock_actual - cantidad_vendida,
            documento_referencia=f"Venta #{instance.Venta.id}",
            usuario="sistema",  # Idealmente debería ser el usuario actual
            precio_unitario=instance.Venta.ImporteTotal / cantidad_vendida if cantidad_vendida else None
        )

        # El stock se actualiza automáticamente por el save() de TransaccionInventario
        producto.FechaUltimaModificacion = timezone.now()
        producto.save()

@receiver(post_save, sender=DetalleCompra)
def actualizar_stock_compra(sender, instance, created, **kwargs):
    """
    Actualiza el stock cuando se realiza una compra
    """
    if created:
        producto = instance.Producto
        cantidad_comprada = instance.Cantidad
        inventario = producto.inventario

        # Registrar la transacción
        TransaccionInventario.objects.create(
            inventario=inventario,
            tipo_movimiento='ENT',
            origen_movimiento='COM',
            cantidad=cantidad_comprada,
            stock_anterior=inventario.stock_actual,
            stock_nuevo=inventario.stock_actual + cantidad_comprada,
            documento_referencia=f"Compra #{instance.Compra.id}",
            usuario="sistema",  # Idealmente debería ser el usuario actual
            precio_unitario=instance.Compra.ImporteTotal / cantidad_comprada if cantidad_comprada else None
        )

        # El stock se actualiza automáticamente por el save() de TransaccionInventario
        producto.FechaUltimaModificacion = timezone.now()
        producto.ultima_compra = timezone.now()
        producto.save()

@receiver(pre_save, sender=TransaccionInventario)
def validar_stock_negativo(sender, instance, **kwargs):
    """
    Evita que el stock se vuelva negativo
    """
    if instance.tipo_movimiento in ['SAL', 'MER']:
        stock_final = instance.inventario.stock_actual - instance.cantidad
        if stock_final < 0:
            raise ValueError("El stock no puede ser negativo")

@receiver(post_save, sender=Producto)
def actualizar_inventario(sender, instance, created, **kwargs):
    """
    Mantiene sincronizado el inventario con el producto
    """
    if created or not hasattr(instance, '_inventario_actualizado'):
        inventario, _ = Inventario.objects.get_or_create(
            producto=instance,
            defaults={
                'stock_actual': instance.Cantidad or 0,
                'stock_minimo': instance.CantidadMinimaSugerida or 0,
            }
        )
        instance._inventario_actualizado = True 