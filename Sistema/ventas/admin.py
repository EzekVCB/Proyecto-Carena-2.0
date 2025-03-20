from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import *
from .generar_datos import *


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('Nombre', 'Apellido', 'DNI', 'Telefono', 'Email', 'Direccion')
    populate_url_name = 'cliente_populate'
    success_message = "Datos ficticios generados correctamente."
    tipo = 'cliente'


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_clients), name='cliente_populate')
        ]
        return custom_urls + urls

    def populate_clients(self, request):
        generar_clientes(5)  # Puedes especificar la cantidad de registros ficticios a generar
        messages.success(request, "Datos ficticios generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'cliente'
        return super(ClienteAdmin, self).changelist_view(request, extra_context=extra_context)


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('RazonSocial', 'CUIT', 'Tel', 'Email', 'Direccion')
    populate_url_name = 'proveedor_populate'
    success_message = "Datos ficticios de proveedores generados correctamente."
    tipo = 'proveedor'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_proveedores), name='proveedor_populate')
        ]
        return custom_urls + urls

    def populate_proveedores(self, request):
        generar_proveedores(5)  # Especifica la cantidad de registros ficticios a generar
        messages.success(request, "Datos ficticios de proveedores generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'proveedor'
        return super(ProveedorAdmin, self).changelist_view(request, extra_context=extra_context)


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_categorias), name='categoria_populate')
        ]
        return custom_urls + urls

    def populate_categorias(self, request):
        generar_categorias(5)
        messages.success(request, "Datos ficticios de categorías generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'categoria'
        return super(CategoriaAdmin, self).changelist_view(request, extra_context=extra_context)

class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('Nombre', 'Categoria')
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_subcategorias), name='subcategoria_populate')
        ]
        return custom_urls + urls

    def populate_subcategorias(self, request):
        generar_subcategorias(5)
        messages.success(request, "Datos ficticios de subcategorías generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'subcategoria'
        return super(SubCategoriaAdmin, self).changelist_view(request, extra_context=extra_context)

class MarcaAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_marcas), name='marca_populate')
        ]
        return custom_urls + urls

    def populate_marcas(self, request):
        generar_marcas(5)
        messages.success(request, "Datos ficticios de marcas generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'marca'
        return super(MarcaAdmin, self).changelist_view(request, extra_context=extra_context)

class UnidadDeMedidaAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_unidades_de_medida), name='unidaddemedida_populate')
        ]
        return custom_urls + urls

    def populate_unidades_de_medida(self, request):
        generar_unidades_de_medida(5)
        messages.success(request, "Datos ficticios de unidades de medida generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'unidaddemedida'
        return super(UnidadDeMedidaAdmin, self).changelist_view(request, extra_context=extra_context)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('Nombre', 'SubCategoria', 'Marca', 'Proveedor', 'CodigoDeBarras', 'Descripcion', 
                   'UnidadDeMedida', 'PrecioCosto', 'PrecioDeLista', 'PrecioDeContado', 'FechaUltimaModificacion')
    search_fields = ('Nombre', 'CodigoDeBarras')
    list_filter = ('SubCategoria', 'Marca', 'Proveedor')
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_productos), name='producto_populate')
        ]
        return custom_urls + urls

    def populate_productos(self, request):
        generar_productos(5)
        messages.success(request, "Datos ficticios de productos generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'producto'
        return super(ProductoAdmin, self).changelist_view(request, extra_context=extra_context)

class MedioDePagoAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_medios_de_pago), name='mediodepago_populate')
        ]
        return custom_urls + urls

    def populate_medios_de_pago(self, request):
        generar_medios_de_pago(5)
        messages.success(request, "Datos ficticios de medios de pago generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'mediodepago'
        return super(MedioDePagoAdmin, self).changelist_view(request, extra_context=extra_context)

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta

class VentaAdmin(admin.ModelAdmin):
    list_display = ('Fecha', 'NumeroComprobate', 'Cliente', 'MedioDePago', 'ImporteTotal')
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_ventas), name='venta_populate')
        ]
        return custom_urls + urls

    def populate_ventas(self, request):
        generar_ventas(5)
        messages.success(request, "Datos ficticios de ventas generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'venta'
        return super(VentaAdmin, self).changelist_view(request, extra_context=extra_context)

    inlines = [
        DetalleVentaInline,
    ]

class DetallePresupuestoInline(admin.TabularInline):
    model = DetallePresupuesto
    
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('Fecha', 'Cliente', 'MedioDePago', 'ImporteTotal')
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_presupuestos), name='presupuesto_populate')
        ]
        return custom_urls + urls

    def populate_presupuestos(self, request):
        generar_presupuestos(5)
        messages.success(request, "Datos ficticios de presupuestos generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'presupuesto'
        return super(PresupuestoAdmin, self).changelist_view(request, extra_context=extra_context)
    
    inlines = [
        DetallePresupuestoInline,
    ]
class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    
class CompraAdmin(admin.ModelAdmin):
    list_display = ('Fecha', 'Proveedor', 'ImporteTotal')
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_compras), name='compra_populate')
        ]
        return custom_urls + urls

    def populate_compras(self, request):
        generar_compras(5)
        messages.success(request, "Datos ficticios de compras generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'compra'
        return super(CompraAdmin, self).changelist_view(request, extra_context=extra_context)
    inlines = [
        DetalleCompraInline,
    ]

class DetalleCuentaInline(admin.TabularInline):
    model = DetalleCuenta
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('Cliente', 'FechaDeAlta', 'FechaDeUltimaModificacion', 'ImporteTotal')
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('populate/', self.admin_site.admin_view(self.populate_cuentas), name='cuenta_populate')
        ]
        return custom_urls + urls

    def populate_cuentas(self, request):
        generar_cuentas(5)
        messages.success(request, "Datos ficticios de cuentas generados correctamente.")
        return redirect('..')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tipo'] = 'cuenta'
        return super(CuentaAdmin, self).changelist_view(request, extra_context=extra_context)
    inlines = [
        DetalleCuentaInline,
    ]

class TransaccionInventarioInline(admin.TabularInline):
    model = TransaccionInventario
    readonly_fields = ('fecha', 'tipo_movimiento', 'origen_movimiento', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'documento_referencia', 'observacion')
    can_delete = False
    extra = 0
    max_num = 0
    ordering = ('-fecha',)

class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'stock_actual', 'stock_minimo', 'stock_maximo', 'ultima_actualizacion', 'estado_stock')
    list_filter = ('producto__SubCategoria', 'producto__Marca')
    search_fields = ('producto__Nombre',)
    readonly_fields = ('ultima_actualizacion',)
    inlines = [TransaccionInventarioInline]
    
    def has_delete_permission(self, request, obj=None):
        return False  # Evita la eliminación de registros de inventario

    fieldsets = (
        ('Información del Producto', {
            'fields': ('producto',)
        }),
        ('Control de Stock', {
            'fields': (('stock_actual', 'stock_minimo', 'stock_maximo'),)
        }),
        ('Información Adicional', {
            'fields': ('ubicacion', 'notas', 'ultima_actualizacion')
        }),
    )

class TransaccionInventarioAdmin(admin.ModelAdmin):
    list_display = ('inventario', 'fecha', 'tipo_movimiento', 'origen_movimiento', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario')
    list_filter = ('tipo_movimiento', 'origen_movimiento', 'fecha', 'inventario__producto__SubCategoria')
    search_fields = ('inventario__producto__Nombre', 'documento_referencia', 'usuario')
    readonly_fields = ('fecha', 'stock_anterior', 'stock_nuevo')
    ordering = ('-fecha',)

class AjusteInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'producto', 'tipo_ajuste', 'cantidad', 'usuario', 'aprobado')
    list_filter = ('tipo_ajuste', 'aprobado', 'fecha', 'producto__SubCategoria')
    search_fields = ('producto__Nombre', 'justificacion', 'usuario')
    readonly_fields = ('fecha', 'fecha_aprobacion')
    ordering = ('-fecha',)

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(SubCategoria, SubCategoriaAdmin)
admin.site.register(Marca, MarcaAdmin)
admin.site.register(UnidadDeMedida, UnidadDeMedidaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(MedioDePago, MedioDePagoAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Presupuesto, PresupuestoAdmin)
admin.site.register(Compra, CompraAdmin)
admin.site.register(Cuenta, CuentaAdmin)
admin.site.register(Inventario, InventarioAdmin)
admin.site.register(TransaccionInventario, TransaccionInventarioAdmin)
admin.site.register(AjusteInventario, AjusteInventarioAdmin)


