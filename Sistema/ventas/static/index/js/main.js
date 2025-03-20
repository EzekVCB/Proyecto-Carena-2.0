/*$( document ).ready(function() {
    // Handler for .ready() called.
    alert('Todo bien');
  });*/


function eliminarEquipo(id) {
  document.getElementById("id_equipo_eliminar").value = id;
}

function eliminarArea(id) {
  document.getElementById("id_area_eliminar").value = id;
}

function marcarBajado(id) {
  document.getElementById("id_trabajo_materiales").value = id;
}

function editarEquipo(id, area, codigo, descripcion) {
  document.getElementById("id_equipo_editar").value = id;
  document.getElementById("area_editar").value = area;
  document.getElementById("codigo_editar").value = codigo;
  document.getElementById("descripcion_editar").value = descripcion;
}

function editarProduct(id, precio, descripcion, costo, cantidad, categoria, servicio) {
  document.getElementById("id_producto_editar").value = id;
  document.getElementById("precio_editar").value = precio;
  document.getElementById("descripcion_editar").value = descripcion;
  document.getElementById("costo_editar").value = costo;
  document.getElementById("cantidad_editar").value = cantidad;
  document.getElementById("categoria_editar").value = categoria;
  if (servicio=='True'){
    document.getElementById('servicio_editar').checked=true;
  }
}

function historialPreventivo(id,solicitadoh,supervisado,responsable, subtotalpiezas, subtotalmo, fecha) {
  
  document.getElementById("hist_preventivo_editar").value = id;
  document.getElementById("hist_solicitadoh").value = solicitadoh;
  document.getElementById("hist_supervisadoh").value = supervisado;
  document.getElementById("hist_responsable").value = responsable;
  document.getElementById("hist_subtotalpiezas").value = subtotalpiezas;
  document.getElementById("hist_subtotalmo").value = subtotalmo;
  document.getElementById("hist_fecha_programada_editar").value = fecha;
}

function editarPreventivo(id, fecha, contacto, piezas, actividades, comentarios, total) {
  
  document.getElementById("id_preventivo_editar").value = id;
  document.getElementById("fecha_editar").value = fecha;
  document.getElementById("contacto_editar").value = contacto;
  document.getElementById("actividades_editar").value = actividades;
  document.getElementById("comentarios_editar").value = comentarios;
  document.getElementById("piezas_editar").value = piezas;
  document.getElementById("total_editar").value = total;
}

function editarCorrectivo(id, equipo, fecha, solicitado, estado, responsable, actividades, subtotalmo, supervisado, falla) {
  
  document.getElementById("id_correctivo_editar").value = id;
  document.getElementById("equipo_editar").value = equipo;
  document.getElementById("fecha_editar").value = fecha;
  document.getElementById("actividades_editar").value = actividades;
  document.getElementById("solicitadoc_editar").value = solicitado;
  document.getElementById("estado_editar").value = estado;
  document.getElementById("responsablec_editar").value = responsable;
  document.getElementById("subtotalmo_editar").value = subtotalmo;
  document.getElementById("supervisadoc_editar").value = supervisado;
  document.getElementById("falla_editar").value = falla;
}

function eliminarCorrectivo(id) {
  document.getElementById("id_correctivo_eliminar").value = id;
}

function historialCorrectivo(id,solicitadoh,supervisado,responsable, subtotalpiezas, subtotalmo, fecha) {

  document.getElementById("hist_correctivo_editar").value = id;
  document.getElementById("hist_solicitadoh").value = solicitadoh;
  document.getElementById("hist_supervisadoh").value = supervisado;
  document.getElementById("hist_responsable").value = responsable;
  document.getElementById("hist_subtotalpiezas").value = subtotalpiezas;
  document.getElementById("hist_subtotalmo").value = subtotalmo;
  document.getElementById("hist_fecha_programada_editar").value = fecha;
}

function eliminarPreventivo(id) {
  document.getElementById("id_preventivo_eliminar").value = id;
}

function eliminarProducto(id) {
  document.getElementById("id_producto_eliminar").value = id;
}

function editarPersonal( id, nombre, apellido, dni, telefono, direccion, email) {

  document.getElementById("id_personal_editar").value = id;
  document.getElementById("nombre_editar").value = nombre;
  document.getElementById("apellido_editar").value = apellido;
  document.getElementById("dni_editar").value = dni;
  document.getElementById("telefono_editar").value = telefono;
  document.getElementById("direccion_editar").value = direccion;
  ocument.getElementById("email_editar").value = email;
}

function eliminarPersonal(id) {
  const campoOculto = document.getElementById("id_personal_eliminar");
  if (campoOculto) {
      campoOculto.value = id;
      console.log("ID asignado correctamente al campo oculto:", id);
  } else {
      console.error("No se encontró el campo oculto con ID 'id_personal_eliminar'.");
  }
  document.getElementById("id_personal_eliminar").value = id;
}

function editarCategoria( id, nombre) {

  document.getElementById("id_categoria_editar").value = id;
  document.getElementById("nombre_editar").value = nombre;
}

function eliminarCategoria(id) {
  const campoOculto = document.getElementById("id_categoria_eliminar");
  if (campoOculto) {
      campoOculto.value = id;
      console.log("ID asignado correctamente al campo oculto:", id);
  } else {
      console.error("No se encontró el campo oculto con ID 'id_categoria_eliminar'.");
  }
  document.getElementById("id_categoria_eliminar").value = id;
}



function borrarContent(){
  document.getElementById("search").value = "";
}

function seleccionarCliente(id, nombre){
 document.getElementById("id_cliente").value = id;
 document.getElementById("cliente").value = nombre;
}

function activarEspera(){
  const btn = document.getElementById("btn");
  btn.innerHTML = 'Generando ... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
  btn.disabled = true;
}

// Configuración por defecto para DataTables (disponible globalmente)
window.defaultDatatableConfig = {
  "language": {
    "url": "//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json"
  },
  "pageLength": 25,
  "responsive": true,
  "autoWidth": false,
  "dom": 'Bfrtip',
  "buttons": [
    {
      extend: 'excel',
      text: '<i class="fas fa-file-excel"></i> Excel',
      className: 'btn btn-success btn-sm',
      exportOptions: {
        columns: ':not(:last-child)'
      }
    },
    {
      extend: 'pdf',
      text: '<i class="fas fa-file-pdf"></i> PDF',
      className: 'btn btn-danger btn-sm',
      exportOptions: {
        columns: ':not(:last-child)'
      }
    },
    {
      extend: 'print',
      text: '<i class="fas fa-print"></i> Imprimir',
      className: 'btn btn-info btn-sm',
      exportOptions: {
        columns: ':not(:last-child)'
      }
    }
  ]
};

// Inicializar DataTables solo si la tabla existe y no está ya inicializada
$(document).ready(function () {
  // Para tablas que necesitan configuración específica
  if ($('#myTable').length && !$.fn.DataTable.isDataTable('#myTable')) {
    $('#myTable').DataTable({
      ...defaultDatatableConfig,
      "order": [[0, "desc"]] // Ordenar primera columna descendente
    });
  }

  if ($('#table2').length && !$.fn.DataTable.isDataTable('#table2')) {
    $('#table2').DataTable({
      ...defaultDatatableConfig,
      "pageLength": 10
    });
  }

  if ($('#table3').length && !$.fn.DataTable.isDataTable('#table3')) {
    $('#table3').DataTable({
      ...defaultDatatableConfig,
      "pageLength": 10
    });
  }
});
 