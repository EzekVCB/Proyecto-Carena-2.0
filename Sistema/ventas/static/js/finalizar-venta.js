// Archivo independiente para finalizar venta
function finalizarVentaDirecto() {
    console.log("Iniciando finalización de venta...");
    
    // Verificar que haya productos en el carrito
    const filas = document.querySelectorAll('#tablaCarrito tbody tr');
    if (filas.length === 0) {
        mostrarErrorEnModal('Debe agregar al menos un producto para realizar la venta');
        return false;
    }
    
    // Verificar que se haya seleccionado un medio de pago principal
    const medioPagoPrincipal = document.getElementById('medio_pago_principal').value;
    if (!medioPagoPrincipal) {
        mostrarErrorEnModal('Debe seleccionar un medio de pago principal');
        return false;
    }
    
    // Verificar que el monto principal sea válido
    const montoPrincipal = parseFloat(document.getElementById('monto_principal').value);
    if (isNaN(montoPrincipal) || montoPrincipal <= 0) {
        mostrarErrorEnModal('El monto del pago principal debe ser mayor a cero');
        return false;
    }
    
    // Si se usa segundo medio de pago, verificar que sea válido
    const usarSegundoMedio = document.getElementById('usar_segundo_medio').checked;
    if (usarSegundoMedio) {
        const medioPagoSecundario = document.getElementById('medio_pago_secundario').value;
        const montoSecundario = parseFloat(document.getElementById('monto_secundario').value);
        
        if (!medioPagoSecundario) {
            mostrarErrorEnModal('Debe seleccionar un medio de pago secundario');
            return false;
        }
        
        if (isNaN(montoSecundario) || montoSecundario <= 0) {
            mostrarErrorEnModal('El monto del pago secundario debe ser mayor a cero');
            return false;
        }
    }
    
    // Verificar que el total de los pagos sea igual al total de la venta
    const totalVenta = parseFloat(document.getElementById('totalVenta').textContent.replace('$', ''));
    let totalPagos = montoPrincipal;
    
    if (usarSegundoMedio) {
        totalPagos += parseFloat(document.getElementById('monto_secundario').value);
    }
    
    if (Math.abs(totalVenta - totalPagos) > 0.01) {
        mostrarErrorEnModal('El total de los pagos debe ser igual al total de la venta');
        return false;
    }
    
    // Crear inputs hidden para los productos
    const productosContainer = document.getElementById('productosSeleccionados');
    productosContainer.innerHTML = ''; // Limpiar contenedor
    
    filas.forEach(function(fila, index) {
        const productoId = fila.getAttribute('data-id');
        const cantidad = fila.querySelector('.cantidad-producto').value;
        const precio = fila.querySelector('.precio-unitario').textContent.replace('$', '');
        
        // Crear inputs hidden
        const inputId = document.createElement('input');
        inputId.type = 'hidden';
        inputId.name = 'productos_ids';
        inputId.value = productoId;
        productosContainer.appendChild(inputId);
        
        const inputCantidad = document.createElement('input');
        inputCantidad.type = 'hidden';
        inputCantidad.name = 'cantidades';
        inputCantidad.value = cantidad;
        productosContainer.appendChild(inputCantidad);
        
        const inputPrecio = document.createElement('input');
        inputPrecio.type = 'hidden';
        inputPrecio.name = 'precios';
        inputPrecio.value = precio;
        productosContainer.appendChild(inputPrecio);
    });
    
    console.log("Enviando formulario...");
    document.getElementById('formVenta').submit();
    return false;
}

// Función para mostrar errores en el modal
function mostrarErrorEnModal(mensaje) {
    const modalBody = document.getElementById('resultadoVentaModalBody');
    modalBody.innerHTML = `
        <div class="text-center">
            <i class="fas fa-exclamation-circle text-danger" style="font-size: 64px;"></i>
            <h4 class="mt-3">Error</h4>
            <p class="mt-3">${mensaje}</p>
        </div>
    `;
    $('#resultadoVentaModal').modal('show');
}
