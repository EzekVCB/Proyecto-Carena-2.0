from django import forms
from .models import Proveedor, Cliente, Producto, Categoria, Venta, PagoVenta  # Asegúrate de importar todos los modelos necesarios
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AddClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['Nombre', 'Apellido', 'DNI', 'Telefono', 'Email', 'Direccion']
        labels = {
            'Nombre': 'Nombre',
            'Apellido': 'Apellido',
            'DNI': 'DNI',
            'Telefono': 'Teléfono',
            'Email': 'Email',
            'Direccion': 'Dirección',
        }

class EditClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['Nombre', 'Apellido', 'DNI', 'Telefono', 'Email', 'Direccion']
        labels = {
            'Nombre': 'Nombre:',
            'Apellido': 'Apellido:',
            'DNI': 'DNI:',
            'Telefono': 'Teléfono:',
            'Email': 'Email:',
            'Direccion': 'Dirección:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'nombre_editar'}),
            'Apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'apellido_editar'}),
            'DNI': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'dni_editar'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'telefono_editar'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'email_editar'}),
            'Direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'direccion_editar'}),
        }

class AddProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['RazonSocial', 'CUIT', 'Tel', 'Email', 'Direccion']
        labels = {
            'RazonSocial': 'Razón Social',
            'CUIT': 'CUIT',
            'Tel': 'Teléfono',
            'Email': 'Email',
            'Direccion': 'Dirección',
        }

class EditProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['RazonSocial', 'CUIT', 'Tel', 'Email', 'Direccion']
        labels = {
            'RazonSocial': 'Razón Social:',
            'CUIT': 'CUIT:',
            'Tel': 'Teléfono:',
            'Email': 'Email:',
            'Direccion': 'Dirección:',
        }

class AddProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'Nombre', 'SubCategoria', 'Marca', 'Proveedor', 'CodigoDeBarras',
            'Descripcion', 'Cantidad', 'CantidadMinimaSugerida',
            'UnidadDeMedida', 'PrecioCosto', 'PrecioDeLista',
            'PrecioDeContado', 'FechaUltimaModificacion'
        ]
        labels = {
            'Nombre': 'Nombre del Producto',
            'SubCategoria': 'Subcategoría',
            'Marca': 'Marca',
            'Proveedor': 'Proveedor',
            'CodigoDeBarras': 'Código de Barras',
            'Descripcion': 'Descripción',
            'Cantidad': 'Cantidad en Stock',
            'CantidadMinimaSugerida': 'Cantidad Mínima Sugerida',
            'UnidadDeMedida': 'Unidad de Medida',
            'PrecioCosto': 'Precio de Costo',
            'PrecioDeLista': 'Precio de Lista',
            'PrecioDeContado': 'Precio de Contado',
            'FechaUltimaModificacion': 'Última Modificación',
        }

class EditProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'Nombre', 'SubCategoria', 'Marca', 'Proveedor', 'CodigoDeBarras',
            'Descripcion', 'Cantidad', 'CantidadMinimaSugerida',
            'UnidadDeMedida', 'PrecioCosto', 'PrecioDeLista',
            'PrecioDeContado', 'FechaUltimaModificacion'
        ]
        labels = {
            'Nombre': 'Nombre del Producto:',
            'SubCategoria': 'Subcategoría:',
            'Marca': 'Marca:',
            'Proveedor': 'Proveedor:',
            'CodigoDeBarras': 'Código de Barras:',
            'Descripcion': 'Descripción:',
            'Cantidad': 'Cantidad en Stock:',
            'CantidadMinimaSugerida': 'Cantidad Mínima Sugerida:',
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
            'Cantidad': forms.NumberInput(attrs={'placeholder': 'Editar cantidad'}),
            'CantidadMinimaSugerida': forms.NumberInput(attrs={'placeholder': 'Editar cantidad mínima sugerida'}),
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
        fields = ['Nombre']
        labels = {
            'Nombre': 'Nombre:',
        }
        widgets = {
            'Nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'nombre_editar'}),
        }

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['Cliente', 'ImporteTotal', 'Caja', 'Cajero']
        # Asegúrate de que MedioDePago no esté aquí

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        }),
        label=""
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        }),
        label=""
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        }),
        label=""
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Personalizar los widgets y quitar las etiquetas
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['username'].label = ""

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password1'].label = ""
        self.fields['password1'].help_text = "La contraseña debe tener al menos 8 caracteres y no puede ser común"

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['password2'].label = ""
        self.fields['password2'].help_text = "Ingresa la misma contraseña para verificar"

class PagoVentaForm(forms.ModelForm):
    class Meta:
        model = PagoVenta
        fields = ['MedioDePago', 'Monto', 'DatosAdicionales']