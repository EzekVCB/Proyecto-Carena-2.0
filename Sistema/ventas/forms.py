from django import forms
from ventas.models import Cliente, Producto, Categoria, AjusteInventario, SubCategoria
from django.utils import timezone

class AddClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['Nombre', 'Apellido', 'DNI', 'Telefono', 'Email', 'Direccion']
        labels = {
            'Nombre': 'Nombre',
            'Apellido': 'Apellido',
            'DNI': 'DNI',
            'Direccion': 'Direccion'
        }

class EditClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields =  ['Nombre', 'Apellido', 'DNI', 'Telefono', 'Email', 'Direccion']
        labels = {
            'Nombre': 'Nombre:',
            'Apellido': 'Apellido:',
            'DNI': 'DNI:',
            'Telefono': 'Teléfono:',
            'Email': 'Email:',
            'Direccion': 'Direccion:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'nombre_editar'}),
            'Apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'apellido_editar'}),
            'DNI': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'dni_editar'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'telefono_editar'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'email_editar'}),
            'Direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'direccion_editar'}),
        }

class AddProductoForm(forms.ModelForm):
    stock_minimo = forms.DecimalField(
        label='Stock Mínimo',
        help_text='Cantidad mínima de stock que debe mantenerse',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
    )
    
    stock_maximo = forms.DecimalField(
        label='Stock Máximo',
        help_text='Cantidad máxima de stock recomendada',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
    )

    class Meta:
        model = Producto
        fields = [
            'Nombre', 'SubCategoria', 'Marca', 'Proveedor', 'CodigoDeBarras',
            'Descripcion', 'UnidadDeMedida', 'PrecioCosto', 'PrecioDeLista',
            'PrecioDeContado', 'FechaUltimaModificacion'
        ]
        labels = {
            'Nombre': 'Nombre del Producto',
            'SubCategoria': 'Subcategoría',
            'Marca': 'Marca',
            'Proveedor': 'Proveedor',
            'CodigoDeBarras': 'Código de Barras',
            'Descripcion': 'Descripción',
            'UnidadDeMedida': 'Unidad de Medida',
            'PrecioCosto': 'Precio de Costo',
            'PrecioDeLista': 'Precio de Lista',
            'PrecioDeContado': 'Precio de Contado',
            'FechaUltimaModificacion': 'Última Modificación',
        }
        widgets = {
            'FechaUltimaModificacion': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'value': timezone.now().strftime('%Y-%m-%d')
                }
            )
        }

class EditProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'Nombre', 'SubCategoria', 'Marca', 'Proveedor', 'CodigoDeBarras', 
            'Descripcion', 'UnidadDeMedida', 'PrecioCosto', 'PrecioDeLista', 
            'PrecioDeContado', 'FechaUltimaModificacion'
        ]
        labels = {
            'Nombre': 'Nombre del Producto:',
            'SubCategoria': 'Subcategoría:',
            'Marca': 'Marca:',
            'Proveedor': 'Proveedor:',
            'CodigoDeBarras': 'Código de Barras:',
            'Descripcion': 'Descripción:',
            'UnidadDeMedida': 'Unidad de Medida:',
            'PrecioCosto': 'Precio de Costo:',
            'PrecioDeLista': 'Precio de Lista:',
            'PrecioDeContado': 'Precio de Contado:',
            'FechaUltimaModificacion': 'Última Modificación:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Editar nombre del producto'}),
            'SubCategoria': forms.Select(attrs={'placeholder': 'Editar subcategoría'}),
            'Marca': forms.Select(attrs={'placeholder': 'Editar marca'}),
            'Proveedor': forms.Select(attrs={'placeholder': 'Editar proveedor'}),
            'CodigoDeBarras': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Editar código de barras'}),
            'Descripcion': forms.Textarea(attrs={'placeholder': 'Editar descripción', 'rows': 3}),
            'UnidadDeMedida': forms.Select(attrs={'placeholder': 'Editar unidad de medida'}),
            'PrecioCosto': forms.NumberInput(attrs={'placeholder': 'Editar precio de costo'}),
            'PrecioDeLista': forms.NumberInput(attrs={'placeholder': 'Editar precio de lista'}),
            'PrecioDeContado': forms.NumberInput(attrs={'placeholder': 'Editar precio de contado'}),
            'FechaUltimaModificacion': forms.DateInput(attrs={'type': 'date'}),
        }


class AddCategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['Nombre']
        labels = {
            'Nombre': 'Nombre',
        }

class EditCategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields =  ['Nombre']
        labels = {
            'Nombre': 'Nombre:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'nombre_editar'}),
        }

class AjusteInventarioForm(forms.ModelForm):
    class Meta:
        model = AjusteInventario
        fields = ['tipo_ajuste', 'cantidad', 'justificacion']
        widgets = {
            'tipo_ajuste': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AddSubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ['Nombre', 'Categoria']
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'Categoria': forms.Select(attrs={'class': 'form-control'})
        }

class EditSubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ['Nombre', 'Categoria']
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'Categoria': forms.Select(attrs={'class': 'form-control'})
        }