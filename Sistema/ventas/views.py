from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages

from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
# from weasyprint.text.fonts import FontConfiguration
from django.template.loader import get_template
# from weasyprint import HTML, CSS
from django.conf import settings
import os
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DecimalField
from django.db.models.functions import ExtractMonth, Now
from django.utils import timezone
from datetime import datetime, time, timedelta
from decimal import Decimal

# Create your views here.

# def index_view(request):
#     context = {
#     }
#     return render(request, 'index.html', context)

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
                messages.info(request, "Cliente agregado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al guardar el cliente: {str(e)}")
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

def ventas_view(request):
    """
    Vista para mostrar la lista de ventas
    """
    ventas = Venta.objects.all().order_by('-Fecha')
    context = {
        'ventas': ventas,
    }
    return render(request, 'ventas.html', context)

def reportes_view(request):
    """
    Vista para la página de reportes
    """
    return render(request, 'reportes.html')
class add_ventas(ListView):
    template_name = 'add_ventas.html'
    model = Egreso

    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request, *args, **kwargs)
    """
    def get_queryset(self):
        return ProductosPreventivo.objects.filter(
            preventivo=self.kwargs['id']
        )
    """
    def post(self, request,*ars, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'autocomplete':
                data = []
                for i in Producto.objects.filter(descripcion__icontains=request.POST["term"])[0:10]:
                    item = i.toJSON()
                    item['value'] = i.descripcion
                    data.append(item)
            else:
                data['error'] = "Ha ocurrido un error"
        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data,safe=False)

def export_pdf_view(request, id, iva):
    #print(id)
    template = get_template("ticket.html")
    #print(id)
    subtotal = 0
    iva_suma = 0

    venta = Egreso.objects.get(pk=float(id))
    datos = ProductosEgreso.objects.filter(egreso=venta)
    for i in datos:
        subtotal = subtotal + float(i.subtotal)
        iva_suma = iva_suma + float(i.iva)

    empresa = "Mi empresa S.A. De C.V"
    context ={
        'num_ticket': id,
        'iva': iva,
        'fecha': venta.fecha_pedido,
        'cliente': venta.cliente.nombre,
        'items': datos,
        'total': venta.total,
        'empresa': empresa,
        'comentarios': venta.comentarios,
        'subtotal': subtotal,
        'iva_suma': iva_suma,
    }
    html_template = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; ticket.pdf"
    css_url = os.path.join(settings.BASE_DIR,'index/static/index/css/bootstrap.min.css')
    #HTML(string=html_template).write_pdf(target="ticket.pdf", stylesheets=[CSS(css_url)])

    # Comentar temporalmente weasyprint
    # from weasyprint.text.fonts import FontConfiguration
    font_config = FontConfiguration()
    HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(target=response, font_config=font_config,stylesheets=[CSS(css_url)])

    return response

def ticket_pdf(request, pk):
    venta = Venta.objects.get(id=pk)
    template = get_template("ventas/ticket.html")
    context = {"venta": venta}
    html_template = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'
    
    # Comentar temporalmente la generación del PDF
    # font_config = FontConfiguration()
    # HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf(target=response, font_config=font_config,stylesheets=[CSS(css_url)])
    
    return response

def obtener_estadisticas_inventario():
    """Obtiene estadísticas generales del inventario"""
    total_productos = Producto.objects.filter(activo=True).count()
    productos_sin_stock = Producto.objects.filter(Cantidad__lte=0).count()
    productos_stock_bajo = Producto.objects.filter(
        Cantidad__gt=0,
        Cantidad__lte=F('CantidadMinimaSugerida')
    ).count()
    valor_total_inventario = Producto.objects.filter(activo=True).aggregate(
        total=Sum(F('Cantidad') * F('PrecioCosto'))
    )['total'] or 0

    return {
        'total_productos': total_productos,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_bajo': productos_stock_bajo,
        'valor_total_inventario': valor_total_inventario
    }

def obtener_productos_criticos():
    """Obtiene lista de productos que necesitan atención"""
    return Producto.objects.filter(
        activo=True
    ).filter(
        Cantidad__lte=F('CantidadMinimaSugerida')
    ).annotate(
        dias_sin_movimiento=ExtractMonth(Now() - F('FechaUltimaModificacion'))
    ).order_by('Cantidad')[:10]

def obtener_movimientos_recientes():
    """Obtiene los últimos movimientos de inventario"""
    return TransaccionInventario.objects.select_related(
        'inventario__producto'
    ).order_by('-fecha')[:10]

def obtener_productos_por_vencer():
    """Obtiene productos próximos a vencer"""
    fecha_limite = datetime.now().date() + timedelta(days=30)
    return Lote.objects.filter(
        fecha_vencimiento__lte=fecha_limite,
        fecha_vencimiento__gte=datetime.now().date(),
        estado='ACTIVO'
    ).select_related('producto').order_by('fecha_vencimiento')[:10]

def dashboard_inventario(request):
    """Vista principal del dashboard de inventario"""
    context = {
        'estadisticas': obtener_estadisticas_inventario(),
        'productos_criticos': obtener_productos_criticos(),
        'movimientos_recientes': obtener_movimientos_recientes(),
        'productos_por_vencer': obtener_productos_por_vencer(),
    }
    return render(request, 'inventario/dashboard.html', context)

def historial_movimientos_producto(request, producto_id):
    """
    Vista para mostrar el historial de movimientos de un producto
    """
    producto = get_object_or_404(Producto, pk=producto_id)
    inventario = producto.inventario
    movimientos = TransaccionInventario.objects.filter(inventario=inventario).order_by('-fecha')
    form = AjusteInventarioForm()

    context = {
        'producto': producto,
        'movimientos': movimientos,
        'form': form,
    }
    return render(request, 'inventario/historial_movimientos.html', context)

def ajuste_inventario(request, producto_id):
    """
    Vista para realizar ajustes manuales al inventario de un producto
    """
    producto = get_object_or_404(Producto, pk=producto_id)
    inventario = producto.inventario

    if request.method == 'POST':
        form = AjusteInventarioForm(request.POST)
        if form.is_valid():
            ajuste = form.save(commit=False)
            ajuste.producto = producto
            ajuste.usuario = request.user.username if request.user.is_authenticated else 'Sistema'
            
            try:
                # Crear la transacción de inventario
                TransaccionInventario.objects.create(
                    inventario=inventario,
                    tipo_movimiento='AJU',
                    origen_movimiento='AJU',
                    cantidad=ajuste.cantidad,
                    stock_anterior=inventario.stock_actual,
                    stock_nuevo=inventario.stock_actual + ajuste.cantidad,
                    documento_referencia=f'Ajuste Manual #{ajuste.id}',
                    usuario=ajuste.usuario,
                    observacion=ajuste.justificacion
                )
                
                # Actualizar el stock del producto
                inventario.stock_actual += ajuste.cantidad
                inventario.save()
                
                ajuste.save()
                messages.success(request, 'Ajuste de inventario realizado correctamente.')
            except Exception as e:
                messages.error(request, f'Error al realizar el ajuste: {str(e)}')
        else:
            messages.error(request, 'Error en el formulario. Por favor, verifica los datos.')
    
    return redirect('historial_movimientos_producto', producto_id=producto_id)





