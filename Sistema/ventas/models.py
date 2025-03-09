from django.db import models
from django.forms import model_to_dict

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
    Cantidad = models.DecimalField(default=None, null=True, max_digits=10, decimal_places=2)
    CantidadMinimaSugerida = models.DecimalField(default=None, null=True, max_digits=10, decimal_places=2)
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
        if self.Cantidad is None or self.CantidadMinimaSugerida is None:
            return "Sin configurar"
        if self.Cantidad <= 0:
            return "Sin stock"
        if self.Cantidad <= self.CantidadMinimaSugerida:
            return "Stock bajo"
        return "Stock normal"

    def necesita_reposicion(self):
        return self.Cantidad <= self.CantidadMinimaSugerida if self.Cantidad and self.CantidadMinimaSugerida else False

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

    def save(self, *args, **kwargs):
        # Actualizar el stock en el inventario
        if not self.pk:  # Solo si es una nueva transacción
            inventario = self.inventario
            if self.tipo_movimiento in ['SAL', 'MER']:
                inventario.stock_actual -= self.cantidad
            else:
                inventario.stock_actual += self.cantidad
            inventario.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Transacción de Inventario"
        verbose_name_plural = "Transacciones de Inventario"
        ordering = ['-fecha']

class AjusteInventario(models.Model):
    TIPO_AJUSTE = [
        ('MER', 'Merma'),
        ('DAÑ', 'Daño'),
        ('ROB', 'Robo'),
        ('VEN', 'Vencimiento'),
        ('ERR', 'Error de Conteo'),
        ('OTR', 'Otro')
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_ajuste = models.CharField(max_length=3, choices=TIPO_AJUSTE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    justificacion = models.TextField()
    usuario = models.CharField(max_length=50)  # Idealmente debería ser ForeignKey a User
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


