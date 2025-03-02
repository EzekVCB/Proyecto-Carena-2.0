from django.db import models
from django.forms import model_to_dict

# Create your models here.
class Cliente(models.Model):
    Nombre = models.CharField(max_length=50, help_text="Nombre del cliente.")
    Apellido = models.CharField(max_length=50)
    DNI = models.CharField(max_length=10)
    Telefono = models.CharField(max_length=20)
    Email = models.EmailField(default=" ")
    Direccion = models.CharField(max_length=50)
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
    def __str__(self):
        return self.Nombre

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


