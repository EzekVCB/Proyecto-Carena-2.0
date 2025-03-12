from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name ='Index'),
    #path('ventas/', views.ventas_view, name='Ventas'),
    #path('ventas/', views.agregar_venta_view, name='AddVenta'),
    path('ventas/', views.add_venta_view, name='AddVenta'),
    path('clientes/', views.clientes_view, name = 'Clientes'),
    path('add_cliente/', views.add_cliente_view, name = 'AddCliente'),
    path('edit_cliente/', views.edit_cliente_view, name = 'EditCliente'),
    path('delete_cliente/', views.delete_cliente_view, name = 'DeleteCliente'),
    path('proveedores/', views.proveedores_view, name='Proveedores'),
    path('add_proveedor/', views.add_proveedor_view, name='AddProveedor'),
    path('edit_proveedor/', views.edit_proveedor_view, name='EditProveedor'),
    path('delete_proveedor/', views.delete_proveedor_view, name='DeleteProveedor'),
    path('productos/', views.productos_view, name = 'Productos'),
    path('add_producto/', views.add_producto_view, name = 'AddProducto'),
    path('edit_producto/', views.edit_producto_view, name = 'EditProducto'),
    path('delete_producto/', views.delete_producto_view, name = 'DeleteProducto'),
    path('categorias/', views.categorias_view, name = 'Categorias'),
    path('add_categoria/', views.add_categoria_view, name = 'AddCategoria'),
    path('edit_categoria/', views.edit_categoria_view, name = 'EditCategoria'),
    path('delete_categoria/', views.delete_categoria_view, name = 'DeleteCategoria'),
    path('login/', views.login_view, name='Login'),
    path('logout/', views.logout_view, name='Logout'),
]