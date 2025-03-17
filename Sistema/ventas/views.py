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
from django.core.paginator import Paginator
from django.db import transaction

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
    caja_abierta = Caja.objects.filter(Cajero=request.user, Estado='ABIERTA').first()
    
    if request.method == 'POST' and caja_abierta:
        try:
            # Obtener datos del formulario
            cliente_id = request.POST.get('cliente_id')
            productos_ids = request.POST.getlist('productos_ids')
            cantidades = request.POST.getlist('cantidades')
            medio_pago_id = request.POST.get('medio_pago_id')
            
            # Montos por método de pago
            monto_efectivo = float(request.POST.get('monto_efectivo', 0))
            monto_qr = float(request.POST.get('monto_qr', 0))
            monto_transferencia = float(request.POST.get('monto_transferencia', 0))
            
            # Validar que hay productos
            if not productos_ids:
                messages.error(request, 'Debe agregar al menos un producto a la venta')
                return redirect('ventas')
            
            # Crear todo en una transacción
            with transaction.atomic():
                # 1. Crear la venta (sin guardar aún)
                venta = Venta()
                venta.Fecha = timezone.now()
                venta.Caja = caja_abierta
                venta.Usuario = request.user
                venta.Cajero = request.user
                
                # Asignar cliente si se seleccionó uno
                if cliente_id:
                    venta.Cliente = Cliente.objects.get(id=cliente_id)
                
                # Generar número de comprobante
                ultimo_comprobante = Venta.objects.order_by('-id').first()
                if ultimo_comprobante:
                    ultimo_numero = int(ultimo_comprobante.NumeroComprobate.split('-')[-1])
                    nuevo_numero = ultimo_numero + 1
                else:
                    nuevo_numero = 1
                
                venta.NumeroComprobate = f"00001-{nuevo_numero:05d}"
                
                # Calcular el total de la venta
                total_venta = 0
                detalles_temp = []  # Almacenar detalles temporalmente
                
                # 2. Preparar los detalles de productos (sin guardar aún)
                for i in range(len(productos_ids)):
                    producto_id = productos_ids[i]
                    cantidad = int(cantidades[i])
                    
                    producto = Producto.objects.get(id=producto_id)
                    
                    # Verificar stock
                    if producto.Cantidad < cantidad:
                        raise Exception(f"No hay suficiente stock para {producto.Nombre}")
                    
                    # Crear detalle (sin guardar aún)
                    detalle = DetalleVenta(
                        Producto=producto,
                        Cantidad=cantidad,
                        PrecioUnitario=producto.PrecioDeContado,
                        Subtotal=producto.PrecioDeContado * cantidad
                    )
                    detalles_temp.append((detalle, producto))
                    
                    # Sumar al total
                    total_venta += detalle.Subtotal
                
                # Asignar el total calculado
                venta.ImporteTotal = total_venta
                
                # 3. AHORA guardamos la venta
                venta.save()
                
                # 4. Guardar los detalles y actualizar stock
                for detalle, producto in detalles_temp:
                    detalle.Venta = venta
                    detalle.save()
                    
                    # Actualizar stock
                    producto.Cantidad -= detalle.Cantidad
                    producto.save()
                
                # 5. Registrar los pagos
                if monto_efectivo > 0:
                    medio_efectivo = MedioDePago.objects.get(Tipo='EFECTIVO')
                    PagoVenta.objects.create(
                        Venta=venta,
                        MedioDePago=medio_efectivo,
                        Monto=monto_efectivo,
                        Fecha=timezone.now()
                    )
                
                if monto_qr > 0:
                    medio_qr = MedioDePago.objects.get(Tipo='QR')
                    PagoVenta.objects.create(
                        Venta=venta,
                        MedioDePago=medio_qr,
                        Monto=monto_qr,
                        Fecha=timezone.now()
                    )
                
                if monto_transferencia > 0:
                    medio_transf = MedioDePago.objects.get(Tipo='TRANSFERENCIA')
                    PagoVenta.objects.create(
                        Venta=venta,
                        MedioDePago=medio_transf,
                        Monto=monto_transferencia,
                        Fecha=timezone.now()
                    )
                
                # El movimiento de caja se creará automáticamente al guardar la venta
                
                messages.success(request, f'Venta #{venta.NumeroComprobate} registrada exitosamente')
                return redirect(f'ventas?venta_exitosa={venta.NumeroComprobate}')
                
        except Exception as e:
            print(f"ERROR GENERAL: {str(e)}")
            messages.error(request, f'Error al procesar la venta: {str(e)}')
            return redirect('ventas')
    
    # Obtener datos para la vista
    context = {
        'caja': caja_abierta
    }
    
    if caja_abierta:
        # Obtener productos con stock
        context['productos'] = Producto.objects.filter(Cantidad__gt=0).order_by('Nombre')
        
        # Obtener clientes
        context['clientes'] = Cliente.objects.all().order_by('Nombre')
        
        # Obtener medios de pago
        context['medios_pago'] = MedioDePago.objects.all()
    
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

@login_required
def caja_view(request):
    # Verificar si hay una caja abierta para este usuario
    caja_abierta = Caja.objects.filter(Cajero=request.user, Estado='ABIERTA').first()
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'abrir':
            # Verificar que no haya otra caja abierta
            if caja_abierta:
                messages.warning(request, "Ya tienes una caja abierta.")
                return redirect('caja')
            
            # Abrir nueva caja
            saldo_inicial = request.POST.get('saldo_inicial')
            try:
                saldo_inicial = decimal.Decimal(saldo_inicial)
                if saldo_inicial < 0:
                    raise ValueError("El saldo inicial no puede ser negativo")
                
                caja = Caja.objects.create(
                    Cajero=request.user,
                    SaldoInicial=saldo_inicial,
                    Estado='ABIERTA'
                )
                messages.success(request, f"Caja #{caja.id} abierta correctamente.")
                return redirect('caja')
            except Exception as e:
                messages.error(request, f"Error al abrir caja: {str(e)}")
        
        elif accion == 'cerrar':
            # Verificar que haya una caja abierta
            if not caja_abierta:
                messages.warning(request, "No tienes una caja abierta para cerrar.")
                return redirect('caja')
            
            # Cerrar caja
            saldo_final_real = request.POST.get('saldo_final_real')
            observaciones = request.POST.get('observaciones', '')
            
            try:
                saldo_final_real = decimal.Decimal(saldo_final_real)
                if saldo_final_real < 0:
                    raise ValueError("El saldo final no puede ser negativo")
                
                caja_abierta.CerrarCaja(saldo_final_real, observaciones)
                messages.success(request, f"Caja #{caja_abierta.id} cerrada correctamente.")
                return redirect('caja')
            except Exception as e:
                messages.error(request, f"Error al cerrar caja: {str(e)}")
    
    # Obtener datos para la vista
    if caja_abierta:
        # Calcular totales
        total_efectivo = caja_abierta.GetTotalEfectivo()
        
        # Debug - imprimir valores
        print(f"DEBUG - Saldo Inicial: {caja_abierta.SaldoInicial}")
        print(f"DEBUG - Total Efectivo: {total_efectivo}")
        print(f"DEBUG - Saldo Esperado: {float(caja_abierta.SaldoInicial) + float(total_efectivo)}")
        
        total_qr = caja_abierta.GetTotalQR()
        total_transferencia = caja_abierta.GetTotalTransferencia()
        total_tarjeta_credito = caja_abierta.GetTotalTarjetaCredito()
        total_tarjeta_debito = caja_abierta.GetTotalTarjetaDebito()
        
        # Calcular saldo esperado en efectivo (saldo inicial + ventas en efectivo)
        saldo_esperado = float(caja_abierta.SaldoInicial) + float(total_efectivo)
        
        # Obtener las ventas asociadas a esta caja
        ventas = Venta.objects.filter(Caja=caja_abierta).order_by('-Fecha')
        
        # Obtener los movimientos de caja
        movimientos = MovimientoCaja.objects.filter(Caja=caja_abierta).order_by('-Fecha')
        
        # Agregar total de ventas al contexto
        total_ventas = caja_abierta.GetTotalVentas()
        
        context = {
            'caja': caja_abierta,
            'total_efectivo': total_efectivo,
            'total_qr': total_qr,
            'total_transferencia': total_transferencia,
            'total_tarjeta_credito': total_tarjeta_credito,
            'total_tarjeta_debito': total_tarjeta_debito,
            'saldo_esperado': saldo_esperado,
            'resumen_por_medio': caja_abierta.GetResumenPorMedioPago(),
            'ventas': ventas,
            'movimientos': movimientos,
            'total_ventas': total_ventas
        }
    else:
        context = {}
    
    return render(request, 'caja.html', context)

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
        cajas = cajas.filter(FechaApertura__date__gte=fecha_inicio)
    
    if fecha_fin:
        cajas = cajas.filter(FechaApertura__date__lte=fecha_fin)
    
    if cajero_id:
        cajas = cajas.filter(Cajero_id=cajero_id)
    
    if estado:
        cajas = cajas.filter(Estado=estado)
    
    # Ordenar por fecha de apertura descendente
    cajas = cajas.order_by('-FechaApertura')
    
    # Obtener lista de cajeros para el filtro
    cajeros = User.objects.filter(is_staff=True)
    
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

@staff_member_required
def detalle_caja_view(request, caja_id):
    """Vista para mostrar el detalle de una caja específica (para AJAX)"""
    try:
        caja = Caja.objects.get(id=caja_id)
        
        # Obtener ventas asociadas a esta caja
        ventas = Venta.objects.filter(Caja=caja).order_by('-Fecha')
        
        # Obtener movimientos de caja
        movimientos = MovimientoCaja.objects.filter(Caja=caja).order_by('-Fecha')
        
        # Calcular totales
        total_efectivo = caja.GetTotalEfectivo()
        total_qr = caja.GetTotalQR()
        total_transferencia = caja.GetTotalTransferencia()
        total_tarjeta_credito = caja.GetTotalTarjetaCredito()
        total_tarjeta_debito = caja.GetTotalTarjetaDebito()
        
        # Calcular saldo esperado en efectivo (saldo inicial + ventas en efectivo)
        saldo_esperado = caja.SaldoInicial + total_efectivo
        
        context = {
            'caja': caja,
            'ventas': ventas,
            'movimientos': movimientos,
            'total_efectivo': total_efectivo,
            'total_qr': total_qr,
            'total_transferencia': total_transferencia,
            'total_tarjeta_credito': total_tarjeta_credito,
            'total_tarjeta_debito': total_tarjeta_debito,
            'saldo_esperado': saldo_esperado,
            'resumen_por_medio': caja.GetResumenPorMedioPago(),
        }
        
        return render(request, 'detalle_caja_ajax.html', context)
    except Caja.DoesNotExist:
        return HttpResponse('<div class="alert alert-danger">La caja solicitada no existe</div>')







