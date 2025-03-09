from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name ='Index'),
    path('ventas/', views.ventas_view, name='Ventas'),
    path('clientes/', views.clientes_view, name = 'Clientes'),
    path('add_cliente/', views.add_cliente_view, name = 'AddCliente'),
    path('edit_cliente/', views.edit_cliente_view, name = 'EditCliente'),
    path('delete_cliente/', views.delete_cliente_view, name = 'DeleteCliente'),
    path('productos/', views.productos_view, name = 'Productos'),
    path('add_producto/', views.add_producto_view, name = 'AddProducto'),
    path('edit_producto/', views.edit_producto_view, name = 'EditProducto'),
    path('delete_producto/', views.delete_producto_view, name = 'DeleteProducto'),
    path('add_venta/',views.add_ventas.as_view(), name='AddVenta'),
    path('export/', views.export_pdf_view, name="ExportPDF" ),
    path('export/<id>/<iva>', views.export_pdf_view, name="ExportPDF" ),
    path('categorias/', views.categorias_view, name = 'Categorias'),
    path('add_categoria/', views.add_categoria_view, name = 'AddCategoria'),
    path('edit_categoria/', views.edit_categoria_view, name = 'EditCategoria'),
    path('delete_categoria/', views.delete_categoria_view, name = 'DeleteCategoria'),
    path('inventario/producto/<int:producto_id>/movimientos/', views.historial_movimientos_producto, name='historial_movimientos_producto'),
    path('inventario/producto/<int:producto_id>/ajuste/', views.ajuste_inventario, name='ajuste_inventario'),
    path('caja/', views.caja_view, name='caja'),
    path('caja/historial/', views.historial_cajas_view, name='historial_cajas'),
    path('caja/<int:caja_id>/', views.detalle_caja_view, name='detalle_caja'),
]