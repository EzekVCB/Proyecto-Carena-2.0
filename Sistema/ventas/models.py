from django.db import models
from django.forms import model_to_dict
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Cliente(models.Model):
    Nombre = models.CharField(max_length=50, help_text="Nombre del cliente.")
    Apellido = models.CharField(max_length=50)
    DNI = models.CharField(max_length=10, null=True, blank=True)
    Telefono = models.CharField(max_length=20, null=True, blank=True)
    Email = models.EmailField(null=True, blank=True)
    Direccion = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.Nombre

class Proveedor(models.Model):
    RazonSocial = models.CharField(max_length=50, help_text="Nombre del proveedor.")
    CUIT = models.CharField(max_length=25)
    Tel = models.CharField(max_length=20)
    Email = models.EmailField(default=" ")
    Direccion = models.CharField(max_length=50)
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
    SubCategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, default=None, null=True)
    Marca = models.ForeignKey(Marca, on_delete=models.CASCADE, default=None, null=True)
    Proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, default=None, null=True)
    CodigoDeBarras = models.CharField(max_length=50)
    Descripcion = models.CharField(max_length=200)
    UnidadDeMedida = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE, default=None, null=True)
    PrecioCosto = models.DecimalField(default=None, null=True, decimal_places=2, max_digits=10)
    PrecioDeLista = models.DecimalField(default=None, null=True, decimal_places=2, max_digits=10)
    PrecioDeContado = models.DecimalField(default=None, null=True, decimal_places=2, max_digits=10)
    FechaUltimaModificacion = models.DateField(null=False)
    activo = models.BooleanField(default=True)  # Para productos descontinuados
    tiempo_reposicion = models.IntegerField(default=1, help_text="Tiempo en días para reponer el producto")
    ultima_compra = models.DateField(null=True, blank=True)
    ultimo_precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def estado_stock(self):
        if not hasattr(self, 'inventario'):
            return "Sin configurar"
        return self.inventario.estado_stock()

    def necesita_reposicion(self):
        if not hasattr(self, 'inventario'):
            return False
        return self.inventario.stock_actual <= self.inventario.stock_minimo

    def __str__(self):
        return self.Nombre

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_maximo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ubicacion = models.CharField(max_length=100, null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Inventario de {self.producto.Nombre}"

    def estado_stock(self):
        if self.stock_actual <= 0:
            return "Sin stock"
        elif self.stock_actual <= self.stock_minimo:
            return "Stock bajo"
        elif self.stock_maximo and self.stock_actual >= self.stock_maximo:
            return "Sobrestock"
        return "Stock normal"

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

class Lote(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=50)
    fecha_fabricacion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    cantidad_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_actual = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_entrada = models.DateField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    factura_compra = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=[
        ('ACTIVO', 'Activo'),
        ('CUARENTENA', 'En Cuarentena'),
        ('VENCIDO', 'Vencido'),
        ('AGOTADO', 'Agotado')
    ], default='ACTIVO')

    def dias_para_vencer(self):
        if self.fecha_vencimiento:
            from datetime import date
            delta = self.fecha_vencimiento - date.today()
            return delta.days
        return None

    def esta_por_vencer(self, dias_alerta=30):
        if self.fecha_vencimiento:
            return 0 < self.dias_para_vencer() <= dias_alerta
        return False

    def __str__(self):
        return f"Lote {self.numero_lote} - {self.producto.Nombre}"

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['fecha_vencimiento']

class TransaccionInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('ENT', 'Entrada'),
        ('SAL', 'Salida'),
        ('AJU', 'Ajuste'),
        ('DEV', 'Devolución')
    ]

    ORIGEN_MOVIMIENTO = [
        ('COM', 'Compra'),
        ('VEN', 'Venta'),
        ('AJU', 'Ajuste Manual'),
        ('DEV', 'Devolución'),
        ('MER', 'Merma'),
        ('INI', 'Inventario Inicial')
    ]

    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='transacciones')
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_movimiento = models.CharField(max_length=3, choices=TIPO_MOVIMIENTO)
    origen_movimiento = models.CharField(max_length=3, choices=ORIGEN_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    stock_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    stock_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    documento_referencia = models.CharField(max_length=50, blank=True, null=True)
    usuario = models.CharField(max_length=50)
    observacion = models.TextField(blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.inventario.producto.Nombre}"

    class Meta:
        verbose_name = "Transacción de Inventario"
        verbose_name_plural = "Transacciones de Inventario"
        ordering = ['-fecha']

class AjusteInventario(models.Model):
    TIPO_AJUSTE = [
        ('ENT', 'Entrada'),
        ('SAL', 'Salida'),
        ('CNT', 'Conteo')
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_ajuste = models.CharField(max_length=3, choices=TIPO_AJUSTE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    justificacion = models.TextField()
    usuario = models.CharField(max_length=50)
    documento_respaldo = models.FileField(upload_to='ajustes/', null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    aprobado_por = models.CharField(max_length=50, null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ajuste de {self.producto.Nombre} - {self.get_tipo_ajuste_display()}"

    class Meta:
        verbose_name = "Ajuste de Inventario"
        verbose_name_plural = "Ajustes de Inventario"
        ordering = ['-fecha']

class MedioDePago(models.Model):
    Nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.Nombre

class Venta(models.Model):
    Fecha = models.DateTimeField(auto_now_add=True)
    NumeroComprobate = models.CharField(max_length=10)
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None, null=True)
    MedioDePago = models.ForeignKey(MedioDePago, on_delete=models.CASCADE, default=None, null=True)
    detalleVentas = models.ManyToManyField(Producto, through="DetalleVenta")
    ImporteTotal = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    def __str__(self):
        return str(self.NumeroComprobate)

class DetalleVenta(models.Model):
    Venta = models.ForeignKey(Venta, on_delete=models.CASCADE, default=None, null=True)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, default=None, null=True)
    Cantidad = models.IntegerField(default=None, null=True)
    def __str__(self):
        venta_str = str(self.Venta) if self.Venta else "No Venta"
        producto_str = str(self.Producto) if self.Producto else "No Producto"
        cantidad_str = str(self.Cantidad) if self.Cantidad is not None else "No Cantidad"
        return f"{venta_str} - {producto_str} - {cantidad_str}"

class Presupuesto(models.Model):
    Fecha = models.DateField(null=False)
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

class Cuenta(models.Model):
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None, null=True)
    FechaDeAlta = models.DateField(null=False)
    FechaDeUltimaModificacion = models.DateField(null=False)
    detalleCuenta = models.ManyToManyField(Producto, through="DetalleCuenta")
    ImporteTotal = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Cuenta de {self.Cliente} - Total: {self.ImporteTotal}"

class DetalleCuenta(models.Model):
    Cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, default=None, null=True)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE, default=None, null=True)
    Cantidad = models.IntegerField(default=None, null=True)
    def __str__(self):
        return f"{self.Cuenta} - {self.Producto} - {self.Cantidad}"

class Egreso(models.Model):
    fecha_pedido = models.DateField(max_length=255)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL , null=True , related_name='cliente')
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    pagado = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    comentarios = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    ticket = models.BooleanField(default=True)
    desglosar = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now_add=True , null=True)

    class Meta:
        verbose_name='egreso'
        verbose_name_plural = 'egresos'
        order_with_respect_to = 'fecha_pedido'

    def __str__(self):
        return str(self.id)

####
class ProductosEgreso(models.Model):
    egreso = models.ForeignKey(Egreso, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=20, decimal_places=2 , null=False)
    precio = models.DecimalField(max_digits=20, decimal_places=2 , null=False , default=0)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2 , null=False , default=0)
    iva = models.DecimalField(max_digits=20, decimal_places=2 , null=False , default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2 , null=False , default=0)
    created = models.DateTimeField(auto_now_add=True)
    entregado = models.BooleanField(default=True)
    devolucion = models.BooleanField(default=False)

    class Meta:
        verbose_name='producto egreso'
        verbose_name_plural = 'productos egreso'
        order_with_respect_to = 'created'

    def __str__(self):
        return self.producto

    def toJSON(self):
        item = model_to_dict(self, exclude=['created'])
        return item

class CajaDiaria(models.Model):
    fecha = models.DateField(auto_now_add=True)
    hora_apertura = models.TimeField(auto_now_add=True)
    hora_cierre = models.TimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_transferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada')
    ], default='ABIERTA')
    usuario_apertura = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cajas_abiertas')
    usuario_cierre = models.ForeignKey(User, on_delete=models.PROTECT, related_name='cajas_cerradas', null=True, blank=True)

    class Meta:
        verbose_name = 'Caja Diaria'
        verbose_name_plural = 'Cajas Diarias'
        ordering = ['-fecha', '-hora_apertura']

    def __str__(self):
        return f'Caja del {self.fecha} - {self.get_estado_display()}'

    def calcular_totales(self):
        # Calcular totales de ventas del día
        ventas_dia = Venta.objects.filter(
            Fecha__date=self.fecha
        )
        
        self.total_ventas = sum(venta.ImporteTotal for venta in ventas_dia)
        self.total_efectivo = sum(venta.ImporteTotal for venta in ventas_dia.filter(MedioDePago__Nombre='EFECTIVO'))
        self.total_tarjeta = sum(venta.ImporteTotal for venta in ventas_dia.filter(MedioDePago__Nombre='TARJETA'))
        self.total_transferencia = sum(venta.ImporteTotal for venta in ventas_dia.filter(MedioDePago__Nombre='TRANSFERENCIA'))
        
        if self.monto_final:
            efectivo_esperado = self.monto_inicial + self.total_efectivo
            self.diferencia = self.monto_final - efectivo_esperado

    def cerrar_caja(self, monto_final, observaciones, usuario):
        if self.estado == 'CERRADA':
            raise ValueError('La caja ya está cerrada')
            
        self.monto_final = monto_final
        self.observaciones = observaciones
        self.estado = 'CERRADA'
        self.hora_cierre = timezone.now().time()
        self.usuario_cierre = usuario
        
        self.calcular_totales()
        self.save()

class MovimientoCaja(models.Model):
    caja = models.ForeignKey(CajaDiaria, on_delete=models.PROTECT, related_name='movimientos')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=[
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso')
    ])
    concepto = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    observacion = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.concepto} - {self.monto}'


