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
    Codigo = models.CharField(max_length=5, unique=True, help_text="Código")
    Nombre = models.CharField(max_length=50, help_text="Nombre del cliente.")
    Apellido = models.CharField(max_length=50)
    DNI = models.CharField(max_length=10, blank=True, null=True)
    Direccion = models.CharField(max_length=50, null=True, blank=True)
    Telefono = models.CharField(max_length=20, null=False, blank=False)
    Email = models.EmailField(default=" ", null=True, blank=True)
    
    class Meta:
        ordering = ['Codigo', 'Nombre', 'Apellido']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"{self.Codigo} - {self.Nombre} {self.Apellido}".strip()
    
    def save(self, *args, **kwargs):
        # Si no se proporciona un código, generar uno automáticamente
        if not self.Codigo:
            # Obtener el último cliente con código numérico
            ultimo_cliente = Cliente.objects.filter(Codigo__regex=r'^\d+$').order_by('-Codigo').first()
            
            if ultimo_cliente and ultimo_cliente.Codigo.isdigit():
                # Incrementar el último código numérico
                nuevo_codigo = int(ultimo_cliente.Codigo) + 1
                # Asegurar que no exceda 9999 (4 dígitos)
                if nuevo_codigo > 9999:
                    nuevo_codigo = 1  # Reiniciar si se excede el límite
                self.Codigo = str(nuevo_codigo).zfill(4)  # Rellenar con ceros a la izquierda
            else:
                # Si no hay códigos numéricos, empezar desde 1
                self.Codigo = '0001'
        
        # Asegurar que el código no exceda 5 caracteres
        if len(self.Codigo) > 5:
            self.Codigo = self.Codigo[:5]
            
        super().save(*args, **kwargs)

class Proveedor(models.Model):
    Codigo = models.CharField(max_length=5, unique=True, help_text="Código")
    RazonSocial = models.CharField(max_length=50, help_text="Nombre del proveedor.")
    CUIT = models.CharField(max_length=25)
    Direccion = models.CharField(max_length=50, null=True, blank=True)
    Tel = models.CharField(max_length=20, null=False, blank=False)
    Email = models.EmailField(default=" ", null=True, blank=True)
    
    class Meta:
        ordering = ['Codigo', 'RazonSocial']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
    
    def __str__(self):
        return f"{self.Codigo} - {self.RazonSocial}".strip()
    
    def save(self, *args, **kwargs):
        # Si no se proporciona un código, generar uno automáticamente
        if not self.Codigo:
            # Obtener el último proveedor con código numérico
            ultimo_proveedor = Proveedor.objects.filter(Codigo__regex=r'^\d+$').order_by('-Codigo').first()
            
            if ultimo_proveedor and ultimo_proveedor.Codigo.isdigit():
                # Incrementar el último código numérico
                nuevo_codigo = int(ultimo_proveedor.Codigo) + 1
                # Asegurar que no exceda 9999 (4 dígitos)
                if nuevo_codigo > 9999:
                    nuevo_codigo = 1  # Reiniciar si se excede el límite
                self.Codigo = str(nuevo_codigo).zfill(4)  # Rellenar con ceros a la izquierda
            else:
                # Si no hay códigos numéricos, empezar desde 1
                self.Codigo = '0001'
        
        # Asegurar que el código no exceda 5 caracteres
        if len(self.Codigo) > 5:
            self.Codigo = self.Codigo[:5]
            
        super().save(*args, **kwargs)

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
    Codigo = models.CharField(max_length=5, unique=True, help_text="Código")
    Nombre = models.CharField(max_length=50)
    SubCategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, null=True, blank=True)
    Marca = models.ForeignKey(Marca, on_delete=models.CASCADE, null=True, blank=True)
    Proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    CodigoDeBarras = models.CharField(max_length=50, null=True, blank=True)
    Descripcion = models.CharField(max_length=200, null=True, blank=True)
    Cantidad = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    CantidadMinimaSugerida = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    UnidadDeMedida = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE, null=True, blank=True)
    PrecioCosto = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    PrecioDeLista = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    PrecioDeContado = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    FechaUltimaModificacion = models.DateField(auto_now=True)
    ProductoOrigen = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='productos_derivados')
    FactorConversion = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    class Meta:
        ordering = ['Codigo', 'Nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return f"{self.Codigo} - {self.Nombre}"
    
    def save(self, *args, **kwargs):
        # Si no se proporciona un código, generar uno automáticamente
        if not self.Codigo or self.Codigo == 'DEFAULT_VALUE':
            # Obtener el último producto con código numérico
            ultimo_producto = Producto.objects.filter(Codigo__regex=r'^\d+$').order_by('-Codigo').first()
            
            if ultimo_producto and ultimo_producto.Codigo.isdigit():
                # Incrementar el último código numérico
                nuevo_codigo = int(ultimo_producto.Codigo) + 1
                # Asegurar que no exceda 9999 (4 dígitos)
                if nuevo_codigo > 9999:
                    nuevo_codigo = 1  # Reiniciar si se excede el límite
                self.Codigo = str(nuevo_codigo).zfill(4)  # Rellenar con ceros a la izquierda
            else:
                # Si no hay códigos numéricos, empezar desde 1
                self.Codigo = '0001'
        
        # Asegurar que el código no exceda 5 caracteres
        if len(self.Codigo) > 5:
            self.Codigo = self.Codigo[:5]
            
        super().save(*args, **kwargs)

    def stock_bajo(self):
        """Verifica si el producto está por debajo del stock mínimo sugerido"""
        return self.Cantidad <= self.CantidadMinimaSugerida
    
    def stock_disponible(self, cantidad_requerida):
        """Verifica si hay suficiente stock disponible"""
        return self.Cantidad >= cantidad_requerida
    
    def get_stock_total(self):
        """
        Obtiene el stock total considerando también el stock del producto origen
        si este producto es derivado
        """
        if not self.ProductoOrigen or not self.FactorConversion:
            return self.Cantidad
        
        # Stock propio
        stock_propio = self.Cantidad
        
        # Stock potencial desde el origen (convertido a unidades de este producto)
        stock_origen = self.ProductoOrigen.Cantidad / self.FactorConversion
        
        return stock_propio + stock_origen
    
    def get_movimientos(self, desde=None, hasta=None):
        """Obtiene los movimientos de stock de este producto en un período"""
        movimientos = self.movimientos.all()
        
        if desde:
            movimientos = movimientos.filter(Fecha__gte=desde)
        if hasta:
            movimientos = movimientos.filter(Fecha__lte=hasta)
            
        return movimientos.order_by('-Fecha')
    
    def get_valor_stock(self):
        """Calcula el valor monetario del stock actual"""
        return self.Cantidad * self.PrecioCosto

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
        
        # Solo guardar la venta, sin crear movimiento
        super().save(*args, **kwargs)

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

ESTADOS_COMPRA = [
    ('PENDIENTE', 'Pendiente'),
    ('PAGADA', 'Pagada'),
]

class Compra(models.Model):
    Fecha = models.DateField(null=False)
    Proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, default=None, null=True)
    DetalleCompra = models.ManyToManyField(Producto, through="DetalleCompra")
    ImporteTotal = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    Estado = models.CharField(max_length=20, choices=ESTADOS_COMPRA, default='PENDIENTE')
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.SET_NULL, null=True, blank=True)  
    FechaPago = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.Fecha} - {self.Estado}"
    
    def get_total_pagado(self):
        """Retorna el total pagado hasta el momento"""
        return self.Pagos.aggregate(total=models.Sum('Monto'))['total'] or 0
    
    def get_saldo_pendiente(self):
        """Retorna el saldo pendiente de pago"""
        return self.ImporteTotal - self.get_total_pagado()
    
    def actualizar_estado(self):
        """Actualiza el estado de la compra según los pagos realizados"""
        total_pagado = self.get_total_pagado()
        
        if total_pagado >= self.ImporteTotal:
            self.Estado = 'PAGADA'
            # Si no tiene fecha de pago, establecer la fecha actual
            if not self.FechaPago:
                self.FechaPago = timezone.now().date()
            self.save()
        else:
            self.Estado = 'PENDIENTE'
            self.save()

class DetalleCompra(models.Model):
    Compra = models.ForeignKey(Compra, on_delete=models.CASCADE, default=None, null=True)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, default=None, null=True)
    Cantidad = models.IntegerField(default=None, null=True)
    PrecioUnitario = models.DecimalField(max_digits=10, decimal_places=2, null=True)
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

class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]
    
    ORIGEN_CHOICES = [
        ('COMPRA', 'Compra'),
        ('VENTA', 'Venta'),
        ('AJUSTE', 'Ajuste de Inventario'),
        ('FRACCIONAMIENTO', 'Fraccionamiento'),
    ]
    
    Fecha = models.DateTimeField(auto_now_add=True)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    Tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    Cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    StockAnterior = models.DecimalField(max_digits=10, decimal_places=2)
    StockResultante = models.DecimalField(max_digits=10, decimal_places=2)
    OrigenMovimiento = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    Detalle = models.CharField(max_length=50, null=True, blank=True, 
                                help_text="ID de la venta, compra, ajuste, etc.")
    Usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    Observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-Fecha']
    
    def __str__(self):
        return f"{self.get_Tipo_display()} - {self.Producto.Nombre} - {self.Cantidad} - {self.Fecha.strftime('%d/%m/%Y %H:%M')}"

class FraccionamientoProducto(models.Model):
    """
    Permite fraccionar un producto en unidades más pequeñas o con diferentes presentaciones.
    Ejemplo: Convertir un tarro grande de detergente en botellas de 1/2 litro y 1 litro.
    """
    Fecha = models.DateTimeField(auto_now_add=True)
    Responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    ProductoOrigen = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='fraccionamientos_origen')
    ProductoDestino = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='fraccionamientos_destino')
    CantidadOrigen = models.DecimalField(max_digits=10, decimal_places=2, 
                                        help_text="Cantidad del producto origen a fraccionar")
    CantidadDestino = models.DecimalField(max_digits=10, decimal_places=2,
                                         help_text="Cantidad del producto destino que se obtiene")
    FactorConversion = models.DecimalField(max_digits=10, decimal_places=4, editable=False,
                                          help_text="Factor de conversión calculado (CantidadDestino/CantidadOrigen)")
    Observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Fraccionamiento de Producto'
        verbose_name_plural = 'Fraccionamientos de Productos'
        ordering = ['-Fecha']
    
    def __str__(self):
        return f"Fraccionamiento #{self.id} - {self.ProductoOrigen.Nombre} a {self.ProductoDestino.Nombre}"
    
    def clean(self):
        """Validaciones adicionales antes de guardar"""
        if self.ProductoOrigen == self.ProductoDestino:
            raise ValidationError("El producto origen y destino no pueden ser el mismo")
        
        if self.CantidadOrigen <= 0 or self.CantidadDestino <= 0:
            raise ValidationError("Las cantidades deben ser mayores que cero")
    
    def save(self, *args, **kwargs):
        es_nuevo = self._state.adding
        
        # Calcular el factor de conversión
        self.FactorConversion = self.CantidadDestino / self.CantidadOrigen
        
        if es_nuevo:
            # Verificar stock suficiente
            if self.ProductoOrigen.Cantidad < self.CantidadOrigen:
                raise ValidationError(f"Stock insuficiente de {self.ProductoOrigen.Nombre}. " 
                                     f"Disponible: {self.ProductoOrigen.Cantidad}, Necesario: {self.CantidadOrigen}")
        
        # Validar el modelo
        self.clean()
        
        super().save(*args, **kwargs)
        
        if es_nuevo:
            # Actualizar stock del producto origen
            stock_anterior_origen = self.ProductoOrigen.Cantidad
            self.ProductoOrigen.Cantidad -= self.CantidadOrigen
            self.ProductoOrigen.save()
            
            # Registrar movimiento de salida
            MovimientoStock.objects.create(
                Producto=self.ProductoOrigen,
                Tipo='SALIDA',
                Cantidad=self.CantidadOrigen,
                StockAnterior=stock_anterior_origen,
                StockResultante=self.ProductoOrigen.Cantidad,
                OrigenMovimiento='FRACCIONAMIENTO',
                Detalle=f"Fraccionamiento #{self.id}",
                Usuario=self.Responsable,
                Observaciones=f"Fraccionamiento a {self.ProductoDestino.Nombre}"
            )
            
            # Actualizar stock del producto destino
            stock_anterior_destino = self.ProductoDestino.Cantidad
            self.ProductoDestino.Cantidad += self.CantidadDestino
            self.ProductoDestino.save()
            
            # Registrar movimiento de entrada
            MovimientoStock.objects.create(
                Producto=self.ProductoDestino,
                Tipo='ENTRADA',
                Cantidad=self.CantidadDestino,
                StockAnterior=stock_anterior_destino,
                StockResultante=self.ProductoDestino.Cantidad,
                OrigenMovimiento='FRACCIONAMIENTO',
                Detalle=f"Fraccionamiento #{self.id}",
                Usuario=self.Responsable,
                Observaciones=f"Fraccionamiento desde {self.ProductoOrigen.Nombre}"
            )

class PagoCompra(models.Model):
    Compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='Pagos')
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.CASCADE)
    Monto = models.DecimalField(max_digits=10, decimal_places=2)
    Fecha = models.DateTimeField(auto_now_add=True)
    DatosAdicionales = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Pago de ${self.Monto} con {self.MedioDePago} para compra #{self.Compra.id}"
    
    def save(self, *args, **kwargs):
        EsNuevo = self._state.adding
        super().save(*args, **kwargs)
        
        # Registrar en caja solo si es un pago nuevo
        if EsNuevo:
            # Obtener la caja abierta
            from django.contrib.auth.models import User
            from django.utils import timezone
            
            # Verificar si hay caja abierta
            cajas_abiertas = Caja.objects.filter(Estado='ABIERTA')
            caja_abierta = cajas_abiertas.first() if cajas_abiertas.exists() else None
            
            if caja_abierta:
                # Buscar si ya existe un campo Compra en MovimientoCaja
                # Si no existe, modificaremos el modelo con una migración después
                from django.db import models
                
                # Crear movimiento de caja
                movimiento = MovimientoCaja.objects.create(
                    Caja=caja_abierta,
                    TipoMovimiento='EGRESO',
                    MontoTotal=self.Monto,
                    Monto=self.Monto,
                    Descripcion=f"Pago {self.MedioDePago} - Compra #{self.Compra.id} a {self.Compra.Proveedor.RazonSocial}",
                    Cajero=caja_abierta.Cajero,
                    MedioDePago=self.MedioDePago
                )
                
                # Actualizar compra
                self.Compra.FechaPago = timezone.now().date()
                
                # Verificar si el pago completa el total
                total_pagado = self.Compra.Pagos.aggregate(total=models.Sum('Monto'))['total'] or 0
                if total_pagado >= self.Compra.ImporteTotal:
                    self.Compra.Estado = 'PAGADA'
                
                self.Compra.save()

