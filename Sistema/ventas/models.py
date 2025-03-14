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
        total_efectivo = self.movimientos.filter(
            tipo_movimiento='INGRESO'
        ).aggregate(
            total=models.Sum('monto_total')
        )['total'] or 0
        
        self.saldo_final_sistema = self.saldo_inicial + total_efectivo
        self.saldo_final_real = saldo_final_real
        self.diferencia = self.saldo_final_real - self.saldo_final_sistema
        self.observaciones = observaciones
        self.fecha_cierre = timezone.now()
        self.estado = 'CERRADA'
        self.save()
        
    def get_total_ventas(self):
        """Retorna el total de ventas realizadas en esta caja"""
        return self.movimientos.filter(
            tipo_movimiento='INGRESO'
        ).aggregate(
            total=models.Sum('monto_total')
        )['total'] or 0
    
    def get_total_efectivo(self):
        """Retorna el total de ventas en efectivo"""
        return self.movimientos.filter(
            tipo_movimiento='INGRESO'
        ).aggregate(
            total=models.Sum('monto_total')
        )['total'] or 0
    
    def get_total_qr(self):
        """Retorna el total de ventas por QR"""
        return self.movimientos.filter(
            tipo_movimiento='INGRESO'
        ).aggregate(
            total=models.Sum('monto_total')
        )['total'] or 0
    
    def get_total_transferencia(self):
        """Retorna el total de ventas por transferencia"""
        return self.movimientos.filter(
            tipo_movimiento='INGRESO'
        ).aggregate(
            total=models.Sum('monto_total')
        )['total'] or 0

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

@login_required
def caja_view(request):
    # Verificar si el usuario tiene una caja abierta
    caja_abierta = Caja.objects.filter(cajero=request.user, estado='ABIERTA').first()
    
    if request.method == 'POST':
        if 'abrir_caja' in request.POST:
            # Verificar que no haya otra caja abierta
            if caja_abierta:
                messages.error(request, "Ya tienes una caja abierta. Debes cerrarla antes de abrir una nueva.")
                return redirect('caja')
            
            try:
                saldo_inicial = request.POST.get('saldo_inicial')
                if not saldo_inicial:
                    messages.error(request, "Debes ingresar un saldo inicial.")
                    return redirect('caja')
                
                # Crear nueva caja
                caja = Caja.objects.create(
                    cajero=request.user,
                    saldo_inicial=saldo_inicial,
                    estado='ABIERTA'
                )
                messages.success(request, f"Caja #{caja.id} abierta exitosamente con saldo inicial de ${saldo_inicial}.")
                return redirect('ventas')  # Redirigir a la pantalla de ventas
                
            except Exception as e:
                messages.error(request, f"Error al abrir la caja: {str(e)}")
                return redirect('caja')
                
        elif 'cerrar_caja' in request.POST:
            if not caja_abierta:
                messages.error(request, "No tienes una caja abierta para cerrar.")
                return redirect('caja')
            
            # Verificar que haya ventas en la caja
            if not caja_abierta.movimientos.exists():
                messages.error(request, "No puedes cerrar la caja sin haber realizado ventas.")
                return redirect('caja')
            
            try:
                saldo_final_real = request.POST.get('saldo_final_real')
                observaciones = request.POST.get('observaciones', '')
                
                if not saldo_final_real:
                    messages.error(request, "Debes ingresar el saldo final real.")
                    return redirect('caja')
                
                # Cerrar la caja
                caja_abierta.cerrar_caja(
                    saldo_final_real=saldo_final_real,
                    observaciones=observaciones
                )
                
                messages.success(request, f"Caja #{caja_abierta.id} cerrada exitosamente.")
                return redirect('index')  # Redirigir al dashboard
                
            except Exception as e:
                messages.error(request, f"Error al cerrar la caja: {str(e)}")
                return redirect('caja')
    
    # Preparar contexto para la plantilla
    context = {}
    
    if caja_abierta:
        # Si hay una caja abierta, mostrar información de la caja
        total_ventas = caja_abierta.get_total_ventas()
        total_efectivo = caja_abierta.get_total_efectivo()
        total_qr = caja_abierta.get_total_qr()
        total_transferencia = caja_abierta.get_total_transferencia()
        
        # Calcular saldo esperado en efectivo
        saldo_esperado = caja_abierta.saldo_inicial + total_efectivo
        
        context = {
            'caja': caja_abierta,
            'total_ventas': total_ventas,
            'total_efectivo': total_efectivo,
            'total_qr': total_qr,
            'total_transferencia': total_transferencia,
            'saldo_esperado': saldo_esperado,
            'movimientos': caja_abierta.movimientos.all().order_by('-fecha')[:10]  # Últimos 10 movimientos
        }

    return render(request, 'caja.html', context)

@login_required
def ventas_view(request):
    # Verificar si hay una caja abierta para este usuario
    caja_abierta = Caja.objects.filter(cajero=request.user, estado='ABIERTA').first()

    if not caja_abierta:
        messages.warning(request, "Debes abrir una caja antes de realizar ventas.")
        return redirect('caja')

    # Continuar con la lógica normal de ventas
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    medios_pago = MedioDePago.objects.all()

    if request.method == 'POST':
        # Procesar la venta
        try:
            cliente_id = request.POST.get('cliente_id')
            medio_pago_id = request.POST.get('medio_pago_id')
            productos_ids = request.POST.getlist('productos_ids')
            cantidades = request.POST.getlist('cantidades')
            
            # Montos por método de pago
            monto = request.POST.get('monto', 0)
            
            # Validar que haya productos
            if not productos_ids:
                messages.error(request, "Debes agregar al menos un producto a la venta.")
                return redirect('ventas')
            
            # Calcular importe total
            importe_total = 0
            for i, producto_id in enumerate(productos_ids):
                producto = Producto.objects.get(id=producto_id)
                cantidad = int(cantidades[i])
                importe_total += producto.PrecioDeContado * cantidad
            
            # Validar que el monto sumen el importe total
            if round(float(monto), 2) != round(float(importe_total), 2):
                messages.error(request, "El monto debe ser igual al importe total.")
                return redirect('ventas')
            
            # Crear la venta
            venta = Venta.objects.create(
                NumeroComprobate=f"V{Venta.objects.count() + 1:06d}",
                Cliente_id=cliente_id if cliente_id else None,
                MedioDePago_id=medio_pago_id,
                ImporteTotal=importe_total,
                caja=caja_abierta,
                cajero=request.user,
                monto=monto
            )
            
            # Crear detalles de venta
            for i, producto_id in enumerate(productos_ids):
                DetalleVenta.objects.create(
                    Venta=venta,
                    Producto_id=producto_id,
                    Cantidad=cantidades[i]
                )
                
                # Actualizar stock del producto
                producto = Producto.objects.get(id=producto_id)
                producto.Cantidad -= int(cantidades[i])
                producto.save()
            
            messages.success(request, f"Venta #{venta.NumeroComprobate} registrada exitosamente.")
            return redirect('ventas')
            
        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {str(e)}")
    
    context = {
        'caja': caja_abierta,
        'productos': productos,
        'clientes': clientes,
        'medios_pago': medios_pago
    }
    
    return render(request, 'ventas.html', context)

@staff_member_required
def historial_cajas_view(request):
    # Filtros
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    cajero_id = request.GET.get('cajero_id')
    estado = request.GET.get('estado')
    
    # Consulta base
    cajas = Caja.objects.all()
    
    # Aplicar filtros
    if fecha_inicio:
        cajas = cajas.filter(fecha_apertura__date__gte=fecha_inicio)
    
    if fecha_fin:
        cajas = cajas.filter(fecha_apertura__date__lte=fecha_fin)
    
    if cajero_id:
        cajas = cajas.filter(cajero_id=cajero_id)
    
    if estado:
        cajas = cajas.filter(estado=estado)
    
    # Ordenar por fecha de apertura descendente
    cajas = cajas.order_by('-fecha_apertura')
    
    # Obtener lista de cajeros para el filtro
    cajeros = User.objects.filter(cajas__isnull=False).distinct()
    
    context = {
        'cajas': cajas,
        'cajeros': cajeros,
        'filtros': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'cajero_id': cajero_id,
            'estado': estado
        }
    }
    
    return render(request, 'historial_cajas.html', context)

