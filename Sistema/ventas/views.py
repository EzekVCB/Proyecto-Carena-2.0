from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages

from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
from weasyprint.text.fonts import FontConfiguration
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.conf import settings
import os
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, time
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

# Create your views here.

def obtener_ventas_del_dia():
    """
    Calcula el total de ventas del día actual.
    Retorna la suma de los montos de todas las ventas realizadas hoy.
    """
    hoy = timezone.now().date()
    inicio_dia = datetime.combine(hoy, time.min)
    fin_dia = datetime.combine(hoy, time.max)

    total_ventas = Venta.objects.filter(
        Fecha__range=(inicio_dia, fin_dia)
    ).aggregate(
        total=Sum('ImporteTotal')
    )['total'] or 0

    return total_ventas

def contar_productos_bajos_stock():
    """
    Cuenta cuántos productos están por debajo de su cantidad mínima sugerida.
    Retorna el número de productos que necesitan reposición.
    """
    productos_bajos = Producto.objects.filter(
        Cantidad__lte=10  # Por ahora usamos un valor fijo de 10 como mínimo
    ).count()

    return productos_bajos

def obtener_productos_stock_bajo():
    """
    Obtiene la lista de productos con stock bajo para mostrar en el dashboard.
    Retorna los 5 productos más críticos en términos de stock.
    """
    productos = Producto.objects.filter(
        Cantidad__lte=10  # Mismo criterio que arriba
    ).order_by('Cantidad')[:5]  # Ordenamos por cantidad ascendente

    return productos

@login_required
def index_view(request):
    context = {
        'ventas_dia': obtener_ventas_del_dia(),
        'productos_bajos': contar_productos_bajos_stock(),
        'total_productos': Producto.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'ultimas_ventas': Venta.objects.all().order_by('-Fecha')[:5],
        'productos_stock_bajo': obtener_productos_stock_bajo(),
    }
    return render(request, 'index.html', context)

def clientes_view(request):
    clientes = Cliente.objects.all()
    form_personal = AddClienteForm()
    form_editar = EditClienteForm()
    context = {
        'clientes': clientes,
        'form_personal': form_personal,
        'form_editar': form_editar,
    }
    return render(request, 'clientes.html', context)

def add_cliente_view(request):
    if request.method == "POST":
        form = AddClienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cliente agregado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al agregar el cliente: {str(e)}")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Clientes')

def edit_cliente_view(request):
    id_personal_editar = request.POST.get('id_personal_editar')
    if id_personal_editar:
        if request.method == "POST":
            cliente = Cliente.objects.get(pk=request.POST.get('id_personal_editar'))
            form = EditClienteForm(request.POST, request.FILES, instance=cliente)
            if form.is_valid():
                try:
                    form.save()
                except Exception as e:
                    messages.success(request, f"Error al modificar el cliente: {str(e)}")
            else:
                messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Clientes')

def delete_cliente_view(request):
    cliente = Cliente.objects.get(pk=request.POST.get('id_personal_eliminar'))
    cliente.delete()
    messages.success(request, "Cliente eliminado exitosamente.")
    return redirect('Clientes')

def proveedores_view(request):
    proveedores = Proveedor.objects.all()
    form_personal = AddProveedorForm()
    form_editar = EditProveedorForm()
    context = {
        'proveedores': proveedores,
        'form_personal': form_personal,
        'form_editar': form_editar,
    }
    return render(request, 'proveedores.html', context)

def add_proveedor_view(request):
    if request.method == "POST":
        form = AddProveedorForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Proveedor agregado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al guardar el proveedor: {str(e)}")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Proveedores')

def edit_proveedor_view(request):
    id_proveedor_editar = request.POST.get('id_proveedor_editar')
    if id_proveedor_editar:
        if request.method == "POST":
            proveedor = Proveedor.objects.get(pk=id_proveedor_editar)
            form = EditProveedorForm(request.POST, instance=proveedor)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Proveedor modificado exitosamente.")
                except Exception as e:
                    messages.error(request, f"Error al modificar el proveedor: {str(e)}")
            else:
                messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Proveedores')

def delete_proveedor_view(request):
    proveedor = Proveedor.objects.get(pk=request.POST.get('id_proveedor_eliminar'))
    proveedor.delete()
    messages.success(request, "Proveedor eliminado exitosamente.")
    return redirect('Proveedores')

@login_required
def productos_view(request):
    productos = Producto.objects.all()
    print(productos)
    form_producto = AddProductoForm()
    form_editar = EditProductoForm()
    context = {
        'productos': productos,
        'form_producto': form_producto,
        'form_editar': form_editar,
    }
    return render(request, 'productos.html', context)

def add_producto_view(request):
    if request.method == "POST":
        form = AddProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto agregado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al guardar el producto: {str(e)}")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Productos')

def edit_producto_view(request):
    if request.method == "POST":
        producto_id = request.POST.get('id_producto_editar')
        producto = get_object_or_404(Producto, pk=producto_id)
        form = EditProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto modificado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al modificar el producto: {str(e)}")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Productos')

def delete_producto_view(request):
    producto = Producto.objects.get(pk=request.POST.get('id_producto_eliminar'))
    producto.delete()
    messages.success(request, "Producto eliminado exitosamente.")
    return redirect('Productos')

@login_required
def categorias_view(request):
    categorias = Categoria.objects.all()
    form_personal = AddCategoriaForm()
    form_editar = EditCategoriaForm()
    context = {
        'categorias': categorias,
        'form_personal': form_personal,
        'form_editar': form_editar,
    }
    return render(request, 'categorias.html', context)

def add_categoria_view(request):
    if request.method == "POST":
        form = AddCategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.info(request, "Categoria agregado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al guardar el categoria: {str(e)}")
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    return redirect('Categorias')

def edit_categoria_view(request):
    print('LLEGUE')
    id_categoria_editar = request.POST.get('id_categoria_editar')
    print(id_categoria_editar)
    if id_categoria_editar:
        if request.method == "POST":
            categoria = Categoria.objects.get(pk=request.POST.get('id_categoria_editar'))
            form = EditCategoriaForm(request.POST, request.FILES, instance=categoria)
            if form.is_valid():
                try:
                    form.save()
                except Exception as e:
                    messages.success(request, f"Error al modificar el ccategorialiente: {str(e)}")
            else:
                messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        messages.error(request, "Error en el formulario. Verifique los datos id_categoria_editar.")
    return redirect('Categorias')

def delete_categoria_view(request):
    print('Estoy en delete')
    categoria = request.POST.get('id_categoria_eliminar')
    if categoria:
        categoria = Categoria.objects.get(pk=request.POST.get('id_categoria_eliminar'))
        categoria.delete()
        messages.success(request, "Categoria eliminado exitosamente.")
    else:
        print('Estoy en deleteCategoria No eliminado.')
    return redirect('Categorias')

#Ventas
@login_required
def ventas_view(request):
    # Verificar si hay una caja abierta para este usuario
    caja_abierta = Caja.objects.filter(cajero=request.user, estado='ABIERTA').first()
    
    if not caja_abierta:
        messages.warning(request, "Debes abrir una caja antes de realizar ventas.")
        return redirect('caja')
    
    # Obtener datos para el formulario
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()
    medios_pago = MedioDePago.objects.all()
    
    if request.method == 'POST':
        # Procesar la venta
        try:
            # Obtener datos del formulario
            cliente_id = request.POST.get('cliente_id')
            medio_pago_id = request.POST.get('medio_pago_id')
            productos_ids = request.POST.getlist('productos_ids')
            cantidades = request.POST.getlist('cantidades')
            
            # Montos por método de pago
            monto_efectivo = float(request.POST.get('monto_efectivo', 0))
            monto_qr = float(request.POST.get('monto_qr', 0))
            monto_transferencia = float(request.POST.get('monto_transferencia', 0))
            
            # Calcular importe total
            importe_total = monto_efectivo + monto_qr + monto_transferencia
            
            # Generar número de comprobante (puedes personalizar esto)
            ultimo_numero = Venta.objects.all().order_by('-id').first()
            if ultimo_numero:
                numero_comprobante = f"{int(ultimo_numero.NumeroComprobate) + 1:010d}"
            else:
                numero_comprobante = "0000000001"
            
            # Crear la venta
            venta = Venta(
                NumeroComprobate=numero_comprobante,
                Cliente_id=cliente_id if cliente_id else None,
                MedioDePago_id=medio_pago_id,
                ImporteTotal=importe_total,
                caja=caja_abierta,
                cajero=request.user,
                monto_efectivo=monto_efectivo,
                monto_qr=monto_qr,
                monto_transferencia=monto_transferencia
            )
            venta.save()
            
            # Crear los detalles de venta
            for i, producto_id in enumerate(productos_ids):
                cantidad = int(cantidades[i])
                producto = Producto.objects.get(id=producto_id)
                
                # Verificar stock
                if producto.Cantidad < cantidad:
                    raise ValidationError(f"Stock insuficiente para {producto.Nombre}")
                
                # Crear detalle
                DetalleVenta.objects.create(
                    Venta=venta,
                    Producto=producto,
                    Cantidad=cantidad,
                    PrecioUnitario=producto.PrecioDeContado,
                    Subtotal=producto.PrecioDeContado * cantidad
                )
                
                # Actualizar stock
                producto.Cantidad -= cantidad
                producto.save()
            
            # Crear movimiento de caja automáticamente
            MovimientoCaja.objects.create(
                caja=caja_abierta,
                tipo_movimiento='INGRESO',
                venta=venta,
                monto_total=importe_total,
                monto_efectivo=monto_efectivo,
                monto_qr=monto_qr,
                monto_transferencia=monto_transferencia,
                descripcion=f"Venta #{numero_comprobante}",
                cajero=request.user
            )
            
            messages.success(request, f"Venta #{numero_comprobante} registrada exitosamente.")
            return redirect('ventas')
            
        except ValidationError as e:
            messages.error(request, str(e))
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

def login_view(request):
    # Redirigir a Index si el usuario ya está autenticado
    if request.user.is_authenticated:
        return redirect('Index')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Redirigir a la página solicitada originalmente o a Index
                next_page = request.GET.get('next', 'Index')
                return redirect(next_page)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('Login')

def register_view(request):
    # Redirigir a Index si el usuario ya está autenticado
    if request.user.is_authenticated:
        return redirect('Index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada para {username}. Ahora puedes iniciar sesión.')
            return redirect('Login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def get_medio_pago_info(request):
    medio_pago_id = request.GET.get('id')
    medio_pago = MedioDePago.objects.get(id=medio_pago_id)
    
    # Determinar el tipo basado en el nombre (o agregar un campo tipo al modelo)
    tipo = 'OTRO'
    if 'efectivo' in medio_pago.Nombre.lower():
        tipo = 'EFECTIVO'
    elif 'qr' in medio_pago.Nombre.lower():
        tipo = 'QR'
    elif 'transferencia' in medio_pago.Nombre.lower():
        tipo = 'TRANSFERENCIA'
    
    return JsonResponse({
        'id': medio_pago.id,
        'nombre': medio_pago.Nombre,
        'tipo': tipo
    })






