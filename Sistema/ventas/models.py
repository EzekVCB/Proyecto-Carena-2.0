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
        ('OTRO', 'Otro'),
    ]
    
    Nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='OTRO')
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.Nombre

class Venta(models.Model):
    Fecha = models.DateTimeField(auto_now_add=True)
    NumeroComprobate = models.CharField(max_length=10)
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None, null=True)
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.CASCADE, default=None, null=False)
    detalleVentas = models.ManyToManyField(Producto, through="DetalleVenta")
    ImporteTotal = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    
    caja = models.ForeignKey('Caja', on_delete=models.PROTECT, null=True, related_name='ventas')
    cajero = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return str(self.NumeroComprobate)
    
    def save(self, *args, **kwargs):
        total_metodos = self.monto
        if total_metodos != self.ImporteTotal:
            raise ValidationError("La suma del monto debe ser igual al importe total")
        
        super().save(*args, **kwargs)
        
        if self.caja and not hasattr(self, '_skip_movimiento'):
            MovimientoCaja.objects.create(
                caja=self.caja,
                tipo_movimiento='INGRESO',
                venta=self,
                monto_total=self.ImporteTotal,
                monto=self.monto,
                descripcion=f"Venta #{self.NumeroComprobate}",
                cajero=self.cajero
            )

class DetalleVenta(models.Model):
    Venta = models.ForeignKey(Venta, on_delete=models.CASCADE, default=None, null=False)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, default=None, null=False)
    Cantidad = models.IntegerField(default=None, null=False)
    def __str__(self):
        venta_str = str(self.Venta) if self.Venta else "No Venta"
        producto_str = str(self.Producto) if self.Producto else "No Producto"
        cantidad_str = str(self.Cantidad) if self.Cantidad is not None else "No Cantidad"
        return f"{venta_str} - {producto_str} - {cantidad_str}"

class Presupuesto(models.Model):
    Fecha = models.DateField(auto_now_add=True)
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None, null=True)
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.CASCADE, default=None, null=True)
    detalleVentas = models.ManyToManyField(Producto, through="DetallePresupuesto")
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
    
    cajero = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cajas')
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_final_sistema = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_final_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ABIERTA')
    
    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['-fecha_apertura']
    
    def __str__(self):
        return f"Caja {self.id} - {self.cajero.username} - {self.fecha_apertura.strftime('%d/%m/%Y %H:%M')}"
    
    def cerrar_caja(self, saldo_final_real, observaciones=None):
        """Cierra la caja calculando la diferencia entre saldo esperado y real"""
        # Calcular el saldo final según el sistema
        total_ventas = self.movimientos.aggregate(
            total=models.Sum('monto_total')
        )['total'] or 0
        
        self.saldo_final_sistema = self.saldo_inicial + total_ventas
        # Convertir el saldo_final_real a decimal
        self.saldo_final_real = decimal.Decimal(str(saldo_final_real))
        self.diferencia = self.saldo_final_real - self.saldo_final_sistema
        self.observaciones = observaciones
        self.fecha_cierre = timezone.now()
        self.estado = 'CERRADA'
        self.save()
        
    def get_total_ventas(self):
        """Retorna el total de ventas de la caja"""
        return self.movimientos.aggregate(total=models.Sum('monto_total'))['total'] or 0
    
    def get_total_efectivo(self):
        """Retorna el total de ventas en efectivo"""
        return self.movimientos.filter(
            venta__MedioDePago__tipo='EFECTIVO'
        ).aggregate(total=models.Sum('monto_total'))['total'] or 0
    
    def get_total_qr(self):
        """Retorna el total de ventas por QR"""
        return self.movimientos.filter(
            venta__MedioDePago__tipo='QR'
        ).aggregate(total=models.Sum('monto_total'))['total'] or 0
    
    def get_total_transferencia(self):
        """Retorna el total de ventas por transferencia"""
        return self.movimientos.filter(
            venta__MedioDePago__tipo='TRANSFERENCIA'
        ).aggregate(total=models.Sum('monto_total'))['total'] or 0

class MovimientoCaja(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_CHOICES, default='INGRESO')
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    cajero = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.monto_total} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

