from django.db import models
from django.forms import model_to_dict
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum

import decimal

# Create your models here.
class Cliente(models.Model):
    Nombre = models.CharField(max_length=50, help_text="Nombre del cliente.")
    Apellido = models.CharField(max_length=50)
    DNI = models.CharField(max_length=10)
    Telefono = models.CharField(max_length=20, null=False, blank=False)
    Email = models.EmailField(default=" ", null=True, blank=True)
    Direccion = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.Nombre

class Proveedor(models.Model):
    RazonSocial = models.CharField(max_length=50, help_text="Nombre del proveedor.")
    CUIT = models.CharField(max_length=25)
    Tel = models.CharField(max_length=20, null=False, blank=False)
    Email = models.EmailField(default=" ", null=True, blank=True)
    Direccion = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.RazonSocial

class Categoria(models.Model):
    Nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.Nombre

class SubCategoria(models.Model):
    Nombre = models.CharField(max_length=50)
    Categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, default=None, null=True)
    def __str__(self):
        return self.Nombre

class Marca(models.Model):
    Nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.Nombre

class UnidadDeMedida(models.Model):
    Nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.Nombre

class Producto(models.Model):
    Nombre = models.CharField(max_length=50)
    Codigo = models.CharField(max_length=10, null=False, blank=False, default='DEFAULT_VALUE')
    SubCategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, default=None, null=True)
    Marca = models.ForeignKey(Marca, on_delete=models.CASCADE, default=None, null=True)
    Proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, default=None, null=True)
    CodigoDeBarras = models.CharField(max_length=50, null=True, blank=True)
    Descripcion = models.CharField(max_length=200, null=True, blank=True)
    Cantidad = models.DecimalField(default=None, null=False, max_digits=10, decimal_places=2)
    CantidadMinimaSugerida = models.DecimalField(default=None, null=False, max_digits=10, decimal_places=2)
    UnidadDeMedida = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE, default=None, null=True)
    PrecioCosto = models.DecimalField(default=None, null=False, decimal_places=2, max_digits=10)
    PrecioDeLista = models.DecimalField(default=None, null=False, decimal_places=2, max_digits=10)
    PrecioDeContado = models.DecimalField(default=None, null=False, decimal_places=2, max_digits=10)
    FechaUltimaModificacion = models.DateField(null=False)
    def __str__(self):
        return self.Nombre

class MedioDePago(models.Model):
    TIPO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('QR', 'QR'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('OTRO', 'Otro'),
    ]
    
    Nombre = models.CharField(max_length=100)
    Tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='EFECTIVO')
    Activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.Nombre

class Venta(models.Model):
    Fecha = models.DateTimeField(auto_now_add=True)
    NumeroComprobate = models.CharField(max_length=10)
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None, null=True)
    DetalleVentas = models.ManyToManyField(Producto, through="DetalleVenta")
    ImporteTotal = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    
    Caja = models.ForeignKey('Caja', on_delete=models.PROTECT, null=True, related_name='Ventas')
    Cajero = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    
    def __str__(self):
        return str(self.NumeroComprobate)
    
    def save(self, *args, **kwargs):
        if not self._state.adding:  # Si no es nueva venta
            total_pagos = self.Pagos.aggregate(total=models.Sum('Monto'))['total'] or 0
            if total_pagos != self.ImporteTotal:
                raise ValidationError("La suma de los pagos debe ser igual al importe total")
        
        super().save(*args, **kwargs)
        
        if self.Caja:  # Eliminar la verificación de _skip_movimiento
            MovimientoCaja.objects.create(
                Caja=self.Caja,
                TipoMovimiento='INGRESO',
                Venta=self,
                MontoTotal=self.ImporteTotal,
                Monto=self.ImporteTotal,
                Descripcion=f"Venta #{self.NumeroComprobate}",
                Cajero=self.Cajero
            )

class DetalleVenta(models.Model):
    Venta = models.ForeignKey(Venta, on_delete=models.CASCADE, default=None, null=False)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, default=None, null=False)
    Cantidad = models.IntegerField(default=None, null=False)
    PrecioUnitario = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    Subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    def __str__(self):
        venta_str = str(self.Venta) if self.Venta else "No Venta"
        producto_str = str(self.Producto) if self.Producto else "No Producto"
        cantidad_str = str(self.Cantidad) if self.Cantidad is not None else "No Cantidad"
        return f"{venta_str} - {producto_str} - {cantidad_str}"

class Presupuesto(models.Model):
    Fecha = models.DateField(auto_now_add=True)
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None, null=True)
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.CASCADE, default=None, null=True)
    DetalleVentas = models.ManyToManyField(Producto, through="DetallePresupuesto")
    ImporteTotal = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    def __str__(self):
        return str(self.Fecha)

class DetallePresupuesto(models.Model):
    Presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, default=None, null=True)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, default=None, null=True)
    Cantidad = models.IntegerField(default=None, null=True)
    def __str__(self):
        return f"{self.Presupuesto} - {self.Producto} - {self.Cantidad}"

class Compra(models.Model):
    Fecha = models.DateField(null=False)
    Proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, default=None, null=True)
    detalleCompra = models.ManyToManyField(Producto, through="DetalleCompra")
    ImporteTotal = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    def __str__(self):
        return str(self.Fecha)

class DetalleCompra(models.Model):
    Compra = models.ForeignKey(Compra, on_delete=models.CASCADE, default=None, null=True)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, default=None, null=True)
    Cantidad = models.IntegerField(default=None, null=True)
    def __str__(self):
        return f"{self.Compra} - {self.Producto} - {self.Cantidad}"

class Caja(models.Model):
    ESTADO_CHOICES = [
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
    ]
    
    Cajero = models.ForeignKey(User, on_delete=models.PROTECT, related_name='Cajas')
    FechaApertura = models.DateTimeField(auto_now_add=True)
    FechaCierre = models.DateTimeField(null=True, blank=True)
    SaldoInicial = models.DecimalField(max_digits=10, decimal_places=2)
    SaldoFinalSistema = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SaldoFinalReal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Observaciones = models.TextField(null=True, blank=True)
    Estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ABIERTA')
    
    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['-FechaApertura']
    
    def __str__(self):
        return f"Caja {self.id} - {self.Cajero.username} - {self.FechaApertura.strftime('%d/%m/%Y %H:%M')}"
    
    def CerrarCaja(self, saldo_final_real, observaciones=None):
        """Cierra la caja calculando la diferencia entre saldo esperado y real"""
        # Calcular el saldo final según el sistema
        saldo_inicial = self.SaldoInicial
        total_efectivo = self.GetTotalEfectivo()
        
        saldo_final_sistema = saldo_inicial + total_efectivo
        diferencia = decimal.Decimal(saldo_final_real) - saldo_final_sistema
        
        # Actualizar datos
        self.FechaCierre = timezone.now()
        self.SaldoFinalSistema = saldo_final_sistema
        self.SaldoFinalReal = saldo_final_real
        self.Diferencia = diferencia
        self.Observaciones = observaciones
        self.Estado = 'CERRADA'
        self.save()
    
    def GetTotalVentas(self):
        """Retorna el total de ventas de la caja"""
        return self.Ventas.aggregate(total=models.Sum('ImporteTotal'))['total'] or 0
    
    def GetTotalEfectivo(self):
        """Calcula el total de ventas en efectivo para esta caja"""
        # Obtener todas las ventas de esta caja
        ventas = Venta.objects.filter(Caja=self)
        
        # Imprimir información de depuración
        print(f"DEBUG - Ventas encontradas: {ventas.count()}")
        
        # Verificar si hay pagos para estas ventas
        for venta in ventas:
            pagos = PagoVenta.objects.filter(Venta=venta)
            print(f"DEBUG - Venta #{venta.id}: {pagos.count()} pagos")
            for pago in pagos:
                print(f"DEBUG - Pago: {pago.MedioDePago} - ${pago.Monto}")
        
        # Obtener los pagos en efectivo de estas ventas
        pagos_efectivo = PagoVenta.objects.filter(
            Venta__in=ventas,
            MedioDePago__Tipo='EFECTIVO'  # Usando el nombre correcto del campo
        ).aggregate(total=Sum('Monto'))['total'] or 0
        
        print(f"DEBUG - Total efectivo calculado (query): {pagos_efectivo}")
        
        # Enfoque alternativo para verificar
        total_efectivo = 0
        for venta in ventas:
            for pago in PagoVenta.objects.filter(Venta=venta):
                if hasattr(pago.MedioDePago, 'Tipo') and pago.MedioDePago.Tipo == 'EFECTIVO':
                    total_efectivo += pago.Monto
        
        print(f"DEBUG - Total efectivo calculado (loop): {total_efectivo}")
        
        return pagos_efectivo  # Usamos el resultado de la consulta
    
    def GetTotalQR(self):
        """Retorna el total de ventas por QR"""
        return self.Movimientos.filter(
            MedioDePago__Tipo='QR'
        ).aggregate(total=models.Sum('MontoTotal'))['total'] or 0
    
    def GetTotalTransferencia(self):
        """Retorna el total de ventas por transferencia"""
        return self.Movimientos.filter(
            MedioDePago__Tipo='TRANSFERENCIA'
        ).aggregate(total=models.Sum('MontoTotal'))['total'] or 0
    
    def GetTotalTarjetaCredito(self):
        """Retorna el total de ventas por tarjeta de crédito"""
        return self.Movimientos.filter(
            MedioDePago__Tipo='TARJETA_CREDITO'
        ).aggregate(total=models.Sum('MontoTotal'))['total'] or 0
    
    def GetTotalTarjetaDebito(self):
        """Retorna el total de ventas por tarjeta de débito"""
        return self.Movimientos.filter(
            MedioDePago__Tipo='TARJETA_DEBITO'
        ).aggregate(total=models.Sum('MontoTotal'))['total'] or 0
    
    def GetResumenPorMedioPago(self):
        """Devuelve un resumen de ventas por medio de pago"""
        resumen = {}
        # Obtener todos los pagos de ventas asociadas a esta caja
        for tipo in MedioDePago.TIPO_CHOICES:
            tipo_id = tipo[0]
            total = self.Movimientos.filter(
                MedioDePago__Tipo=tipo_id
            ).aggregate(total=Sum('MontoTotal'))['total'] or 0
            
            resumen[tipo[1]] = total
            
        return resumen

class MovimientoCaja(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]
    
    Caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='Movimientos')
    Fecha = models.DateTimeField(auto_now_add=True)
    TipoMovimiento = models.CharField(max_length=10, choices=TIPO_CHOICES, default='INGRESO')
    Venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    MontoTotal = models.DecimalField(max_digits=10, decimal_places=2)
    Monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Descripcion = models.CharField(max_length=255, null=True, blank=True)
    Cajero = models.ForeignKey(User, on_delete=models.PROTECT)
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-Fecha']
    
    def __str__(self):
        return f"{self.get_TipoMovimiento_display()} - {self.MontoTotal} - {self.Fecha.strftime('%d/%m/%Y %H:%M')}"

class PagoVenta(models.Model):
    Venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='Pagos')
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.CASCADE)
    Monto = models.DecimalField(max_digits=10, decimal_places=2)
    Fecha = models.DateTimeField(auto_now_add=True)
    DatosAdicionales = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Pago de ${self.Monto} con {self.MedioDePago} para venta #{self.Venta.NumeroComprobate}"
    
    def save(self, *args, **kwargs):
        EsNuevo = self._state.adding
        super().save(*args, **kwargs)
        
        # Registrar en caja
        if EsNuevo and self.Venta.Caja:
            MovimientoCaja.objects.create(
                Caja=self.Venta.Caja,
                TipoMovimiento='INGRESO',
                Venta=self.Venta,
                MontoTotal=self.Monto,
                Monto=self.Monto,
                Descripcion=f"Pago {self.MedioDePago} - Venta #{self.Venta.NumeroComprobate}",
                Cajero=self.Venta.Cajero,
                MedioDePago=self.MedioDePago
            )

