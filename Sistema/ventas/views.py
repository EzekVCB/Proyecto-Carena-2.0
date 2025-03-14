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
def add_venta_view(request):
    productos = Producto.objects.all()  # Obtener todos los productos
    if request.method == "POST":
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)  # No guardar aún
            venta.save()  # Guardar la venta
            # Aquí puedes agregar lógica para guardar los detalles de la venta
            for producto_id in request.POST.getlist('productos'):
                producto = Producto.objects.get(id=producto_id)
                detalle = DetalleVenta(Venta=venta, Producto=producto, Cantidad=request.POST.get(f'cantidad_{producto_id}'))
                detalle.save()
            messages.success(request, "Venta agregada exitosamente.")
            return redirect('Ventas')  # Redirigir a la lista de ventas
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = VentaForm()
    return render(request, 'add_ventas.html', {'form': form, 'productos': productos})

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






