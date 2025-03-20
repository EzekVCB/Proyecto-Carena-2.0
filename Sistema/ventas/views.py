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
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse

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
    # Usar el método de filtrado directo en la base de datos
    productos_bajos = Producto.objects.filter(
        Cantidad__lte=models.F('CantidadMinimaSugerida')
    ).count()

    return productos_bajos

def obtener_productos_stock_bajo():
    """
    Obtiene la lista de productos con stock bajo para mostrar en el dashboard.
    Retorna los 5 productos más críticos en términos de stock.
    """
    # Usar el método de filtrado directo en la base de datos
    productos = Producto.objects.filter(
        Cantidad__lte=models.F('CantidadMinimaSugerida')
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
                proveedor = form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Si es una solicitud AJAX, devolver JSON
                    proveedores = Proveedor.objects.all()
                    return JsonResponse({
                        'success': True,
                        'message': 'Proveedor agregado exitosamente.',
                        'nuevo_proveedor_id': proveedor.id,
                        'proveedores': [{'id': p.id, 'RazonSocial': p.RazonSocial} for p in proveedores]
                    })
                else:
                    messages.success(request, "Proveedor agregado exitosamente.")
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Error al guardar el proveedor: {str(e)}'
                    })
                messages.error(request, f"Error al guardar el proveedor: {str(e)}")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario. Verifique los datos ingresados.'
                })
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
        try:
            nombre = request.POST.get('Nombre')
            categoria = Categoria.objects.create(Nombre=nombre)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Si es una solicitud AJAX, devolver JSON con las categorías actualizadas
                categorias = Categoria.objects.all()
                return JsonResponse({
                    'success': True,
                    'message': 'Categoría agregada exitosamente.',
                    'nueva_categoria_id': categoria.id,
                    'categorias': [{'id': c.id, 'Nombre': c.Nombre} for c in categorias]
                })
            else:
                messages.success(request, "Categoría agregada exitosamente.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al guardar la categoría: {str(e)}'
                })
            messages.error(request, f"Error al guardar la categoría: {str(e)}")
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
        print("\n=== INICIO PROCESAMIENTO VENTA ===")
        print(f"Usuario: {request.user.username}")
        print(f"Datos POST: {request.POST}")
        
        try:
            # Obtener datos del formulario
            cliente_id = request.POST.get('cliente_id')
            productos_ids = request.POST.getlist('productos_ids')
            cantidades = request.POST.getlist('cantidades')
            precios = request.POST.getlist('precios')
            medio_pago_principal_id = request.POST.get('medio_pago_principal')
            monto_principal = request.POST.get('monto_principal')
            medio_pago_secundario_id = request.POST.get('medio_pago_secundario')
            monto_secundario = request.POST.get('monto_secundario')
            fecha_comprobante = request.POST.get('fecha_comprobante')
            tipo_ticket = request.POST.get('imprimir_ticket', 'no')
            
            print(f"Productos IDs: {productos_ids}")
            print(f"Cantidades: {cantidades}")
            print(f"Precios: {precios}")
            
            # Validar que hay productos
            if not productos_ids:
                messages.error(request, 'Debe agregar al menos un producto a la venta')
                return redirect('ventas')
            
            # Crear todo en una transacción
            with transaction.atomic():
                # 1. Crear la venta (sin guardar aún)
                venta = Venta()
                
                # Usar la fecha del comprobante si se proporciona
                if fecha_comprobante:
                    try:
                        fecha_dt = datetime.strptime(fecha_comprobante, '%Y-%m-%d')
                        venta.Fecha = make_aware(fecha_dt)
                    except:
                        venta.Fecha = timezone.now()
                else:
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
                
                # Agregar prefijo según tipo de ticket
                prefijo = "F" if tipo_ticket == "fiscal" else "N"
                venta.NumeroComprobate = f"{prefijo}-{nuevo_numero:05d}"
                
                # Calcular el total de la venta
                total_venta = 0
                detalles_temp = []
                
                # 2. Preparar los detalles de productos (sin guardar aún)
                for i in range(len(productos_ids)):
                    producto_id = productos_ids[i]
                    cantidad = int(cantidades[i])
                    precio = float(precios[i])
                    
                    producto = Producto.objects.get(id=producto_id)
                    
                    # Verificar stock
                    if producto.Cantidad < cantidad:
                        raise Exception(f"No hay suficiente stock para {producto.Nombre}")
                    
                    # Crear detalle (sin guardar aún)
                    detalle = DetalleVenta(
                        Producto=producto,
                        Cantidad=cantidad,
                        PrecioUnitario=precio,
                        Subtotal=precio * cantidad
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
                if medio_pago_principal_id:
                    try:
                        medio_pago_principal = MedioDePago.objects.get(id=medio_pago_principal_id)
                        
                        # Si no se especificó un monto para el medio principal, usar el total
                        if not monto_principal or float(monto_principal) <= 0:
                            monto_principal = total_venta
                        else:
                            monto_principal = float(monto_principal)
                        
                        # Verificar si hay un segundo medio de pago
                        if medio_pago_secundario_id and monto_secundario and float(monto_secundario) > 0:
                            monto_secundario = float(monto_secundario)
                            
                            # Validar que la suma de los montos sea igual al total
                            if abs((monto_principal + monto_secundario) - total_venta) > 0.01:
                                # Ajustar el monto principal para que sumen exactamente el total
                                monto_principal = total_venta - monto_secundario
                            
                            # Crear el pago con el medio secundario
                            medio_pago_secundario = MedioDePago.objects.get(id=medio_pago_secundario_id)
                            PagoVenta.objects.create(
                                Venta=venta,
                                MedioDePago=medio_pago_secundario,
                                Monto=monto_secundario,
                                Fecha=timezone.now()
                            )
                        
                        # Crear el pago con el medio principal
                        PagoVenta.objects.create(
                            Venta=venta,
                            MedioDePago=medio_pago_principal,
                            Monto=monto_principal,
                            Fecha=timezone.now()
                        )
                    except Exception as e:
                        print(f"ERROR AL PROCESAR PAGOS: {str(e)}")
                        messages.error(request, f'Error al procesar los pagos: {str(e)}')
                        # Revertir la transacción en caso de error
                        transaction.set_rollback(True)
                        return redirect('ventas')
                else:
                    messages.error(request, 'Debe seleccionar al menos un medio de pago')
                    # Revertir la transacción en caso de error
                    transaction.set_rollback(True)
                    return redirect('ventas')
                
                # El movimiento de caja se creará automáticamente al guardar la venta
                
                messages.success(request, f'Venta #{venta.NumeroComprobate} registrada exitosamente')
                return redirect(reverse('ventas') + f'?venta_exitosa={venta.NumeroComprobate}')
                
        except Exception as e:
            print(f"ERROR GENERAL: {str(e)}")
            messages.error(request, f'Error al procesar la venta: {str(e)}')
            return redirect('ventas')
    
    # Obtener datos para la vista
    context = {
        'caja': caja_abierta,
        'today': timezone.now()  # Para establecer la fecha actual en el campo
    }
    
    if caja_abierta:
        # Obtener productos con stock
        context['productos'] = Producto.objects.filter(Cantidad__gt=0).order_by('Nombre')
        
        # Obtener clientes
        context['clientes'] = Cliente.objects.all().order_by('Nombre')
        
        # Obtener medios de pago
        context['medios_pago'] = MedioDePago.objects.all()
        
        # Buscar el medio de pago "Efectivo"
        try:
            medio_efectivo = MedioDePago.objects.filter(Nombre__icontains='efectivo').first()
            if medio_efectivo:
                context['medio_efectivo_id'] = medio_efectivo.id
        except:
            pass
        
        # Sugerir el siguiente número de comprobante
        ultimo_comprobante = Venta.objects.order_by('-id').first()
        if ultimo_comprobante:
            ultimo_numero = int(ultimo_comprobante.NumeroComprobate.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
            prefijo = ultimo_comprobante.NumeroComprobate.split('-')[0]
            context['ultimo_comprobante'] = f"{prefijo}-{nuevo_numero:05d}"
    
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

# Agregar esta vista para guardar clientes mediante AJAX
@csrf_exempt
def guardar_cliente_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente = Cliente(
                Nombre=data['nombre'],
                Apellido=data['apellido'],
                DNI=data.get('dni', ''),
                Telefono=data.get('telefono', ''),
                Email=data.get('email', ''),
                Direccion=data.get('direccion', '')
            )
            cliente.save()
            return JsonResponse({
                'success': True,
                'cliente_id': cliente.id
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# Vistas para Historial de Movimientos de Stock
@login_required
def historial_movimientos(request):
    form = BusquedaMovimientosForm(request.GET or None)
    
    # Consulta base
    movimientos = MovimientoStock.objects.all()
    
    # Aplicar filtros si el formulario es válido
    if form.is_valid():
        producto = form.cleaned_data.get('producto')
        tipo = form.cleaned_data.get('tipo')
        origen = form.cleaned_data.get('origen')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        
        if producto:
            movimientos = movimientos.filter(Producto=producto)
        if tipo:
            movimientos = movimientos.filter(Tipo=tipo)
        if origen:
            movimientos = movimientos.filter(OrigenMovimiento=origen)
        if fecha_desde:
            movimientos = movimientos.filter(Fecha__date__gte=fecha_desde)
        if fecha_hasta:
            movimientos = movimientos.filter(Fecha__date__lte=fecha_hasta)
    
    # Ordenar por fecha descendente
    movimientos = movimientos.order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(movimientos, 50)
    page = request.GET.get('page')
    movimientos_paginados = paginator.get_page(page)
    
    context = {
        'form': form,
        'movimientos': movimientos_paginados,
    }
    
    return render(request, 'ventas/historial_movimientos.html', context)

# Vistas para Ajustes de Inventario
@login_required
def lista_ajustes(request):
    ajustes = AjusteInventario.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(ajustes, 20)
    page = request.GET.get('page')
    ajustes_paginados = paginator.get_page(page)
    
    context = {
        'ajustes': ajustes_paginados,
    }
    
    return render(request, 'ventas/lista_ajustes.html', context)

@login_required
def crear_ajuste(request):
    if request.method == 'POST':
        form = AjusteInventarioForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Crear el ajuste pero no guardarlo aún
                ajuste = form.save(commit=False)
                ajuste.Usuario = request.user
                
                # Guardar el ajuste
                ajuste.save()
                
                messages.success(request, "Ajuste de inventario creado. Ahora agregue los detalles.")
                return redirect('detalle_ajuste', ajuste_id=ajuste.id)
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = AjusteInventarioForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_ajuste.html', context)

@login_required
def detalle_ajuste(request, ajuste_id):
    ajuste = get_object_or_404(AjusteInventario, pk=ajuste_id)
    detalles = DetalleAjuste.objects.filter(Ajuste=ajuste)
    
    if request.method == 'POST':
        form = DetalleAjusteForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    detalle = form.save(commit=False)
                    detalle.Ajuste = ajuste
                    detalle.CantidadAnterior = detalle.Producto.Cantidad
                    detalle.save()
                    
                    messages.success(request, "Detalle agregado correctamente.")
                    return redirect('detalle_ajuste', ajuste_id=ajuste.id)
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = DetalleAjusteForm()
    
    context = {
        'ajuste': ajuste,
        'detalles': detalles,
        'form': form,
    }
    
    return render(request, 'ventas/detalle_ajuste.html', context)

# Vistas para Inventario Físico
@login_required
def lista_inventarios(request):
    inventarios = InventarioFisico.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(inventarios, 20)
    page = request.GET.get('page')
    inventarios_paginados = paginator.get_page(page)
    
    context = {
        'inventarios': inventarios_paginados,
    }
    
    return render(request, 'ventas/lista_inventarios.html', context)

@login_required
def crear_inventario(request):
    if request.method == 'POST':
        form = InventarioFisicoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Crear el inventario pero no guardarlo aún
                inventario = form.save(commit=False)
                inventario.Usuario = request.user
                inventario.Estado = 'BORRADOR'
                
                # Guardar el inventario
                inventario.save()
                
                messages.success(request, "Inventario físico creado. Ahora agregue los productos.")
                return redirect('detalle_inventario', inventario_id=inventario.id)
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = InventarioFisicoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_inventario.html', context)

@login_required
def detalle_inventario(request, inventario_id):
    inventario = get_object_or_404(InventarioFisico, pk=inventario_id)
    
    # Si el inventario no está en estado borrador, no permitir modificaciones
    if inventario.Estado != 'BORRADOR':
        messages.warning(request, "Este inventario ya está finalizado y no puede ser modificado.")
        return redirect('lista_inventarios')
    
    detalles = DetalleInventarioFisico.objects.filter(Inventario=inventario)
    
    if request.method == 'POST':
        # Verificar si es una solicitud para agregar un producto
        if 'agregar_producto' in request.POST:
            producto_id = request.POST.get('producto')
            
            # Verificar si el producto ya está en el inventario
            if DetalleInventarioFisico.objects.filter(Inventario=inventario, Producto_id=producto_id).exists():
                messages.error(request, "Este producto ya está en el inventario.")
            else:
                try:
                    producto = Producto.objects.get(pk=producto_id)
                    
                    # Crear el detalle con la cantidad del sistema
                    DetalleInventarioFisico.objects.create(
                        Inventario=inventario,
                        Producto=producto,
                        CantidadSistema=producto.Cantidad,
                        CantidadFisica=0  # Inicialmente 0, el usuario debe ingresar la cantidad real
                    )
                    
                    messages.success(request, f"Producto {producto.Nombre} agregado al inventario.")
                except Producto.DoesNotExist:
                    messages.error(request, "Producto no encontrado.")
        
        # Verificar si es una solicitud para actualizar la cantidad física
        elif 'actualizar_cantidad' in request.POST:
            detalle_id = request.POST.get('detalle_id')
            cantidad_fisica = request.POST.get('cantidad_fisica')
            
            try:
                detalle = DetalleInventarioFisico.objects.get(pk=detalle_id, Inventario=inventario)
                detalle.CantidadFisica = cantidad_fisica
                detalle.save()
                
                messages.success(request, f"Cantidad actualizada para {detalle.Producto.Nombre}.")
            except DetalleInventarioFisico.DoesNotExist:
                messages.error(request, "Detalle no encontrado.")
        
        # Verificar si es una solicitud para finalizar el inventario
        elif 'finalizar_inventario' in request.POST:
            try:
                inventario.finalizar(request.user)
                messages.success(request, "Inventario finalizado y ajustes aplicados correctamente.")
                return redirect('lista_inventarios')
            except ValidationError as e:
                messages.error(request, str(e))
    
    # Obtener productos que no están en el inventario para el selector
    productos_en_inventario = detalles.values_list('Producto_id', flat=True)
    productos_disponibles = Producto.objects.exclude(id__in=productos_en_inventario).order_by('Nombre')
    
    context = {
        'inventario': inventario,
        'detalles': detalles,
        'productos_disponibles': productos_disponibles,
    }
    
    return render(request, 'ventas/detalle_inventario.html', context)

# Vistas para Transferencias entre Productos
@login_required
def lista_transferencias(request):
    transferencias = TransferenciaProducto.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(transferencias, 20)
    page = request.GET.get('page')
    transferencias_paginadas = paginator.get_page(page)
    
    context = {
        'transferencias': transferencias_paginadas,
    }
    
    return render(request, 'ventas/lista_transferencias.html', context)

@login_required
def crear_transferencia(request):
    if request.method == 'POST':
        form = TransferenciaProductoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    transferencia = form.save(commit=False)
                    transferencia.Usuario = request.user
                    transferencia.Estado = 'PENDIENTE'
                    transferencia.save()
                    
                    messages.success(request, "Transferencia creada correctamente.")
                    return redirect('lista_transferencias')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = TransferenciaProductoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_transferencia.html', context)

@login_required
def completar_transferencia(request, transferencia_id):
    transferencia = get_object_or_404(TransferenciaProducto, pk=transferencia_id)
    
    try:
        transferencia.completar()
        messages.success(request, "Transferencia completada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_transferencias')

@login_required
def cancelar_transferencia(request, transferencia_id):
    transferencia = get_object_or_404(TransferenciaProducto, pk=transferencia_id)
    
    try:
        transferencia.cancelar()
        messages.success(request, "Transferencia cancelada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_transferencias')

# Vistas para Reservas de Stock
@login_required
def lista_reservas(request):
    reservas = ReservaStock.objects.all().order_by('-Fecha')
    
    # Paginación
    paginator = Paginator(reservas, 20)
    page = request.GET.get('page')
    reservas_paginadas = paginator.get_page(page)
    
    context = {
        'reservas': reservas_paginadas,
    }
    
    return render(request, 'ventas/lista_reservas.html', context)

@login_required
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaStockForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Verificar stock disponible
                    producto = form.cleaned_data['Producto']
                    cantidad = form.cleaned_data['Cantidad']
                    
                    if not producto.stock_disponible(cantidad):
                        raise ValidationError(f"Stock insuficiente para {producto.Nombre}")
                    
                    # Crear la reserva
                    reserva = form.save(commit=False)
                    reserva.Usuario = request.user
                    reserva.Estado = 'ACTIVA'
                    reserva.save()
                    
                    messages.success(request, "Reserva creada correctamente.")
                    return redirect('lista_reservas')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Error en el formulario. Verifique los datos ingresados.")
    else:
        form = ReservaStockForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/crear_reserva.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(ReservaStock, pk=reserva_id)
    
    try:
        reserva.cancelar()
        messages.success(request, "Reserva cancelada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_reservas')

@login_required
def utilizar_reserva(request, reserva_id):
    reserva = get_object_or_404(ReservaStock, pk=reserva_id)
    
    try:
        reserva.utilizar()
        messages.success(request, "Reserva marcada como utilizada correctamente.")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('lista_reservas')

# Función para obtener subcategorías según la categoría seleccionada
def get_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    subcategorias = []
    categorias = list(Categoria.objects.all().values('id', 'Nombre'))
    
    if categoria_id:
        try:
            subcategorias = list(SubCategoria.objects.filter(Categoria_id=categoria_id).values('id', 'Nombre'))
        except Exception as e:
            print(f"Error al obtener subcategorías: {str(e)}")
    
    return JsonResponse({
        'subcategorias': subcategorias,
        'categorias': categorias
    })

# Función para agregar subcategorías
def add_subcategoria_view(request):
    if request.method == "POST":
        try:
            categoria = Categoria.objects.get(pk=request.POST.get('Categoria'))
            nombre = request.POST.get('Nombre')
            subcategoria = SubCategoria.objects.create(
                Nombre=nombre,
                Categoria=categoria
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Obtener todas las subcategorías de la categoría seleccionada
                subcategorias = SubCategoria.objects.filter(Categoria=categoria)
                return JsonResponse({
                    'success': True,
                    'message': 'Subcategoría creada correctamente',
                    'subcategoria': {
                        'id': subcategoria.id,
                        'nombre': subcategoria.Nombre
                    },
                    'subcategorias': [{'id': s.id, 'Nombre': s.Nombre} for s in subcategorias]
                })
            messages.success(request, "Subcategoría agregada exitosamente.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al guardar la subcategoría: {str(e)}'
                })
            messages.error(request, f"Error al guardar la subcategoría: {str(e)}")
    return redirect('Productos')

# Función para obtener marcas
def get_marcas(request):
    try:
        marcas = list(Marca.objects.all().values('id', 'Nombre'))
        return JsonResponse({'success': True, 'marcas': marcas})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para obtener proveedores
def get_proveedores(request):
    try:
        proveedores = list(Proveedor.objects.all().values('id', 'RazonSocial'))
        return JsonResponse({'success': True, 'proveedores': proveedores})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para obtener unidades de medida
def get_unidades(request):
    try:
        unidades = list(UnidadDeMedida.objects.all().values('id', 'Nombre'))
        return JsonResponse({'success': True, 'unidades': unidades})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para obtener datos de un producto
def get_producto(request):
    try:
        producto_id = request.GET.get('id')
        producto = Producto.objects.get(pk=producto_id)
        
        data = {
            'Nombre': producto.Nombre,
            'Descripcion': producto.Descripcion,
            'Marca': producto.Marca.id if producto.Marca else None,
            'Proveedor': producto.Proveedor.id if producto.Proveedor else None,
            'categoria': producto.SubCategoria.Categoria.id if producto.SubCategoria else None,
            'SubCategoria': producto.SubCategoria.id if producto.SubCategoria else None,
            'PrecioCosto': float(producto.PrecioCosto),
            'PrecioDeLista': float(producto.PrecioDeLista),
            'PrecioDeContado': float(producto.PrecioDeContado),
            'Cantidad': float(producto.Cantidad),
            'CantidadMinimaSugerida': float(producto.CantidadMinimaSugerida),
            'UnidadDeMedida': producto.UnidadDeMedida.id if producto.UnidadDeMedida else None,
            'FechaUltimaModificacion': producto.FechaUltimaModificacion.strftime('%Y-%m-%d') if producto.FechaUltimaModificacion else None
        }
        
        return JsonResponse({'success': True, 'producto': data})
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Función para agregar marcas
def add_marca_view(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get('Nombre')
            marca = Marca.objects.create(Nombre=nombre)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': marca.id,
                    'nombre': marca.Nombre
                })
            messages.success(request, "Marca agregada exitosamente.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error al guardar la marca: {str(e)}")
    return redirect('Productos')

# Función para agregar unidades de medida
def add_unidad_view(request):
    if request.method == "POST":
        try:
            nombre = request.POST.get('Nombre')
            unidad = UnidadDeMedida.objects.create(Nombre=nombre)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': unidad.id,
                    'nombre': unidad.Nombre
                })
            messages.success(request, "Unidad de medida agregada exitosamente.")
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error al guardar la unidad de medida: {str(e)}")
    return redirect('Productos')

# Funciones para gestión de compras
def compras_view(request):
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            proveedor_id = request.POST.get('proveedor')
            fecha = request.POST.get('fecha')
            estado = request.POST.get('estado', 'PENDIENTE')  # Default a 'PENDIENTE'
            medio_pago_id = request.POST.get('medio_pago')
            fecha_pago = request.POST.get('fecha_pago')
            
            # Crear la compra
            compra = Compra.objects.create(
                Fecha=fecha,
                Proveedor_id=proveedor_id,
                ImporteTotal=0,
                Estado=estado.upper()  # Asegurar que esté en mayúsculas
            )
            
            # Si la compra está pagada, actualizar medio de pago y fecha
            if estado.upper() == 'PAGADA' and medio_pago_id and fecha_pago:
                compra.MedioDePago_id = medio_pago_id
                compra.FechaPago = fecha_pago
                compra.save()
            
            # Procesar los detalles de la compra
            total = 0
            productos = request.POST.getlist('producto[]')
            cantidades = request.POST.getlist('cantidad[]')
            precios = request.POST.getlist('precio[]')
            
            for producto_id, cantidad, precio in zip(productos, cantidades, precios):
                if producto_id and cantidad and precio:
                    producto = Producto.objects.get(pk=producto_id)
                    cantidad = int(cantidad)
                    precio = float(precio)
                    
                    # Actualizar el precio de costo solo si el nuevo precio es mayor
                    if precio > producto.PrecioCosto:
                        producto.PrecioCosto = precio
                        
                        # Calcular los nuevos precios de venta (30% y 40% de ganancia)
                        precio_lista = precio * 1.30  # 30% de ganancia
                        precio_contado = precio * 1.40  # 40% de ganancia
                        
                        # Actualizar los precios del producto
                        producto.PrecioDeLista = precio_lista
                        producto.PrecioDeContado = precio_contado
                        producto.FechaUltimaModificacion = fecha
                    
                    # Actualizar el stock
                    producto.Cantidad += cantidad
                    producto.save()
                    
                    # Crear el detalle de compra con el precio unitario
                    DetalleCompra.objects.create(
                        Compra=compra,
                        Producto=producto,
                        Cantidad=cantidad,
                        PrecioUnitario=precio
                    )
                    
                    total += precio * cantidad
            
            # Actualizar el total de la compra
            compra.ImporteTotal = total
            compra.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Si es GET, mostrar el formulario
    proveedores = Proveedor.objects.all()
    productos = Producto.objects.all()
    medios_pago = MedioDePago.objects.all()
    
    context = {
        'proveedores': proveedores,
        'productos': productos,
        'medios_pago': medios_pago,
    }
    return render(request, 'compras.html', context)

def lista_compras(request):
    compras = Compra.objects.all().order_by('-Fecha')
    medios_pago = MedioDePago.objects.all()
    proveedores = Proveedor.objects.all()
    productos = Producto.objects.all()
    
    return render(request, 'lista_compras.html', {
        'compras': compras,
        'medios_pago': medios_pago,
        'proveedores': proveedores,
        'productos': productos
    })

def detalles_compra(request):
    try:
        compra_id = request.GET.get('compra_id')
        detalles = DetalleCompra.objects.filter(Compra_id=compra_id)
        
        detalles_json = []
        for detalle in detalles:
            detalles_json.append({
                'producto': detalle.Producto.Nombre,
                'cantidad': detalle.Cantidad,
                'precio_unitario': float(detalle.PrecioUnitario) if detalle.PrecioUnitario else 0
            })
        
        return JsonResponse({
            'success': True,
            'detalles': detalles_json
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def actualizar_pago_compra(request):
    if request.method == 'POST':
        try:
            compra_id = request.POST.get('compra_id')
            medio_pago_id = request.POST.get('medio_pago')
            fecha_pago = request.POST.get('fecha_pago')
            
            compra = Compra.objects.get(id=compra_id)
            compra.Estado = 'PAGADA'
            compra.MedioDePago_id = medio_pago_id
            compra.FechaPago = fecha_pago
            compra.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Pago registrado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

def registrar_pago(request):
    if request.method == 'POST':
        try:
            medio_pago_id = request.POST.get('medio_pago')
            fecha_pago = request.POST.get('fecha_pago')
            
            # Solo validamos que los datos del pago sean correctos
            if not medio_pago_id or not fecha_pago:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe completar todos los campos del pago'
                })
            
            return JsonResponse({
                'success': True,
                'message': 'Datos de pago validados correctamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

def editar_compra(request):
    if request.method == 'POST':
        try:
            compra_id = request.POST.get('compra_id')
            compra = Compra.objects.get(id=compra_id)
            
            # Guardar los detalles antiguos para actualizar el stock
            detalles_antiguos = {detalle.Producto_id: detalle.Cantidad for detalle in DetalleCompra.objects.filter(Compra=compra)}
            
            # Actualizar datos básicos de la compra
            compra.Fecha = request.POST.get('fecha')
            compra.Proveedor_id = request.POST.get('proveedor')
            compra.Estado = request.POST.get('estado')
            
            # Si está pagada, actualizar datos de pago
            if compra.Estado == 'PAGADA':
                compra.MedioDePago_id = request.POST.get('medio_pago')
                compra.FechaPago = request.POST.get('fecha_pago')
            
            # Eliminar detalles antiguos
            DetalleCompra.objects.filter(Compra=compra).delete()
            
            # Procesar nuevos detalles
            total = 0
            productos = request.POST.getlist('producto[]')
            cantidades = request.POST.getlist('cantidad[]')
            precios = request.POST.getlist('precio[]')
            
            productos_actualizados = []
            
            for producto_id, cantidad, precio in zip(productos, cantidades, precios):
                if producto_id and cantidad and precio:
                    producto = Producto.objects.get(pk=producto_id)
                    cantidad = int(cantidad)
                    precio = float(precio)
                    
                    # Restar la cantidad antigua del stock
                    cantidad_antigua = detalles_antiguos.get(int(producto_id), 0)
                    producto.Cantidad -= cantidad_antigua
                    
                    # Sumar la nueva cantidad
                    producto.Cantidad += cantidad
                    
                    # Actualizar el precio de costo solo si el nuevo precio es mayor
                    if precio > producto.PrecioCosto:
                        producto.PrecioCosto = precio
                        # Calcular los nuevos precios de venta
                        precio_lista = precio * 1.30
                        precio_contado = precio * 1.40
                        
                        # Actualizar los precios del producto
                        producto.PrecioDeLista = precio_lista
                        producto.PrecioDeContado = precio_contado
                        producto.FechaUltimaModificacion = compra.Fecha
                    
                    producto.save()
                    
                    # Agregar información del producto actualizado
                    productos_actualizados.append({
                        'nombre': producto.Nombre,
                        'stock_actual': producto.Cantidad
                    })
                    
                    # Crear el nuevo detalle con el precio unitario
                    DetalleCompra.objects.create(
                        Compra=compra,
                        Producto=producto,
                        Cantidad=cantidad,
                        PrecioUnitario=precio
                    )
                    
                    total += precio * cantidad
            
            # Actualizar el total de la compra
            compra.ImporteTotal = total
            compra.save()
            
            return JsonResponse({
                'success': True,
                'stock_actualizado': True,
                'productos_actualizados': productos_actualizados
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def obtener_detalles_compra(request):
    try:
        compra_id = request.GET.get('compra_id')
        if not compra_id:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionó ID de compra'
            })

        compra = Compra.objects.get(id=compra_id)
        detalles = DetalleCompra.objects.filter(Compra=compra)
        
        detalles_json = []
        for detalle in detalles:
            detalles_json.append({
                'producto_id': detalle.Producto.id,
                'cantidad': detalle.Cantidad,
                'precio_unitario': float(detalle.PrecioUnitario) if detalle.PrecioUnitario else 0
            })
        
        return JsonResponse({
            'success': True,
            'compra': {
                'fecha': compra.Fecha.strftime('%Y-%m-%d'),
                'proveedor_id': compra.Proveedor.id,
                'estado': compra.Estado,
                'medio_pago_id': compra.MedioDePago.id if compra.MedioDePago else None,
                'fecha_pago': compra.FechaPago.strftime('%Y-%m-%d') if compra.FechaPago else None
            },
            'detalles': detalles_json
        })
    except Compra.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'La compra no existe'
        })
    except Exception as e:
        print(f"Error en obtener_detalles_compra: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener los detalles: {str(e)}'
        })

def eliminar_compra(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            compra_id = data.get('compra_id')
            compra = Compra.objects.get(id=compra_id)
            
            # Obtener los detalles de la compra antes de eliminarla
            detalles = DetalleCompra.objects.filter(Compra=compra)
            productos_actualizados = []
            
            # Actualizar el stock de cada producto
            for detalle in detalles:
                producto = detalle.Producto
                # Restar la cantidad del stock ya que se está eliminando la compra
                producto.Cantidad -= detalle.Cantidad
                producto.save()
                productos_actualizados.append({
                    'nombre': producto.Nombre,
                    'stock_actual': producto.Cantidad
                })
            
            # Eliminar la compra
            compra.delete()
            
            return JsonResponse({
                'success': True,
                'stock_actualizado': True,
                'productos_actualizados': productos_actualizados
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})







