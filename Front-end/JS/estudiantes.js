/**
 * estudiantes.js - Sistema de Gestión UNPHU
 * Regla: URL Base sin barra final para concatenar rutas limpias
 */
const API = "https://black-box-bryr.onrender.com";

let modoEdicion = false;
let idEditando = null;

// 1. CARGA DE LA TABLA PRINCIPAL
function cargarEstudiantes() {
    // Sincronizado con Swagger: GET /estudiantes/
    fetch(`${API}/estudiantes/`) 
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaEstudiantes tbody");
        if (!tabla) return;
        tabla.innerHTML = "";
        
        // Manejo de respuesta (Array directo según Swagger)
        const estudiantes = Array.isArray(data) ? data : (data.estudiantes || []);

        estudiantes.forEach(e => {
            tabla.innerHTML += `
            <tr>
                <td>${e.id_unphu}</td>
                <td>${e.nombre}</td>
                <td>${e.correo_institucional || 'N/A'}</td>
                <td>${e.nombre_carrera || e.codigo_carrera}</td> 
                <td class="${e.estado_activo === 'Activo' ? 'estado-activa' : 'estado-inactiva'}">
                    <strong>${e.estado_activo}</strong>
                </td>
                <td>
                    <button class="btn-editar" onclick="editarEstudiante('${e.id_unphu}')">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarEstudiante('${e.id_unphu}')">Eliminar</button>
                </td>
            </tr>`;
        });
    })
    .catch(err => console.error("Error al cargar lista:", err));
}

// 2. FUNCIÓN DE EDICIÓN (LA QUE FALTABA)
function editarEstudiante(id) {
    // Abrimos el modal de inmediato y damos feedback
    abrirModal();
    const title = document.getElementById("modalTitle");
    if (title) title.textContent = "Cargando datos...";

    // REGLA: encodeURIComponent para IDs con caracteres especiales
    // Según Swagger: GET /estudiantes/{id_unphu} no lleva barra final
    fetch(`${API}/estudiantes/${encodeURIComponent(id)}`)
    .then(res => {
        if (!res.ok) throw new Error("No se pudo obtener el estudiante");
        return res.json();
    })
    .then(data => {
        const e = data.estudiante || data.data || data;
        
        // Llenado de campos con los IDs de tu HTML
        document.getElementById("id_unphu").value = e.id_unphu;
        document.getElementById("nombre").value = e.nombre;
        document.getElementById("correo_institucional").value = e.correo_institucional || "";
        document.getElementById("codigo_carrera").value = e.codigo_carrera;
        document.getElementById("estado_activo").value = e.estado_activo;

        // Bloqueo de ID UNPHU (No editable)
        document.getElementById("id_unphu").disabled = true;
        if (title) title.textContent = "Editar Estudiante";

        modoEdicion = true;
        idEditando = id;
    })
    .catch(err => {
        alert("Error: " + err.message);
        cerrarModal();
    });
}

// 3. GUARDAR CAMBIOS (POST/PUT)
document.getElementById("crearEstudianteForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const payload = {
        id_unphu: document.getElementById("id_unphu").value,
        nombre: document.getElementById("nombre").value,
        codigo_carrera: document.getElementById("codigo_carrera").value, 
        estado_activo: document.getElementById("estado_activo").value,
        correo_institucional: document.getElementById("correo_institucional").value || null
    };

    let url = `${API}/estudiantes/`; // POST /estudiantes/
    let method = "POST";
    let bodyData = JSON.stringify(payload);

    if (modoEdicion) {
        url = `${API}/estudiantes/${encodeURIComponent(idEditando)}`; 
        method = "PUT";
        // REGLA CRÍTICA: No enviar ID en el cuerpo si es PUT
        const { id_unphu, ...updateData } = payload;
        bodyData = JSON.stringify(updateData);
    }

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: bodyData
    })
    .then(async res => {
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "Error en el servidor");
        }
        return res.json();
    })
    .then(() => {
        alert(modoEdicion ? "Estudiante actualizado" : "Estudiante creado");
        cargarEstudiantes();
        cerrarModal();
    })
    .catch(err => alert("Error al guardar: " + err.message));
});

// 4. ELIMINAR ESTUDIANTE
function eliminarEstudiante(id) {
    if (!confirm(`¿Estás seguro de eliminar la matrícula ${id}?`)) return;

    // Sincronizado: DELETE /estudiantes/{id_unphu}
    fetch(`${API}/estudiantes/${encodeURIComponent(id)}`, { 
        method: "DELETE" 
    })
    .then(res => {
        if (res.ok) {
            alert("Eliminado correctamente");
            cargarEstudiantes();
        } else {
            alert("Error al eliminar. Verifique ruteo y CORS.");
        }
    })
    .catch(err => alert("Failed to fetch: Problema de red."));
}

// 5. GESTIÓN DE MODAL (ESTÁNDAR DE ORO)
function abrirModal() {
    const modal = document.getElementById("modalEstudiante");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open"); // Bloqueo de scroll
    }
}

function cerrarModal() {
    const modal = document.getElementById("modalEstudiante");
    if (modal) modal.style.display = "none";
    document.body.classList.remove("modal-open");
    document.getElementById("crearEstudianteForm").reset();
    document.getElementById("id_unphu").disabled = false;
    modoEdicion = false;
    idEditando = null;
}

// 6. CARGAR CARRERAS (VALOR = CÓDIGO)
function cargarCarreras() {
    fetch(`${API}/carreras/`)
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("codigo_carrera");
        if (!select) return;
        select.innerHTML = '<option value="">Seleccione Carrera</option>';
        const carreras = Array.isArray(data) ? data : (data.carreras || []);
        carreras.forEach(c => {
            // value es el código corto que espera el backend
            select.innerHTML += `<option value="${c.codigo}">${c.nombre}</option>`;
        });
    });
}

// INICIALIZACIÓN
document.addEventListener("DOMContentLoaded", () => {
    cargarEstudiantes();
    cargarCarreras();
});

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById("modalEstudiante");
    if (event.target == modal) cerrarModal();
}