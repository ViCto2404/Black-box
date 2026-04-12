/**
 * directores.js - Sistema de Gestión UNPHU
 * Regla: URL Base sin barra final para ruteo dinámico
 */
const API = "https://black-box-bryr.onrender.com";

let modoEdicion = false;
let idEditando = null;

// 1. CARGA DE LISTADO
function cargarDirectores() {
    // Sincronizado con Swagger: GET /directores/
    fetch(`${API}/directores/`) 
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaDirectores tbody");
        if (!tabla) return;
        tabla.innerHTML = "";
        
        // Manejo de respuesta de array directo según el router
        const directores = Array.isArray(data) ? data : (data.directores || []);

        directores.forEach(d => {
            tabla.innerHTML += `
            <tr>
                <td>${d.id_unphu}</td>
                <td>${d.nombre}</td>
                <td>${d.correo_institucional}</td>
                <td>${d.nombre_escuela || d.codigo_escuela || "N/A"}</td>
                <td>
                    <button class="btn-editar" onclick="editarDirector('${d.id_unphu}')">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarDirector('${d.id_unphu}')">Eliminar</button>
                </td>
            </tr>`;
        });
    })
    .catch(err => console.error("Error cargando directores:", err));
}

// 2. FUNCIÓN DE EDICIÓN
function editarDirector(id) {
    // Primero activamos el modo edición para que abrirModal no lo sobreescriba
    modoEdicion = true;
    idEditando = id;
    
    abrirModal();
    const title = document.getElementById("modalTitle");
    if (title) title.textContent = "Cargando datos...";

    // Sincronizado: GET /directores/{id} sin barra final
    fetch(`${API}/directores/${encodeURIComponent(id)}`) 
    .then(res => res.json())
    .then(d => {
        // Llenado de campos según tu modelo DirectorCreate
        document.getElementById("id_unphu").value = d.id_unphu;
        document.getElementById("nombre").value = d.nombre;
        document.getElementById("correo_institucional").value = d.correo_institucional;
        document.getElementById("codigo_escuela").value = d.codigo_escuela || "";

        // REGLA: El ID no es editable en modo PUT
        document.getElementById("id_unphu").disabled = true;
        if (title) title.textContent = "Editar Director";
    })
    .catch(err => {
        alert("Error al cargar datos del director.");
        cerrarModal();
    });
}

// 3. LOGICA DE GUARDADO (CREAR Y ACTUALIZAR)
document.getElementById("crearDirectorForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const payload = {
        id_unphu: document.getElementById("id_unphu").value,
        nombre: document.getElementById("nombre").value,
        correo_institucional: document.getElementById("correo_institucional").value,
        codigo_escuela: document.getElementById("codigo_escuela").value || null
    };

    let url = `${API}/directores/`; // POST /directores/
    let method = "POST";
    let bodyData = JSON.stringify(payload);

    if (modoEdicion) {
        // PUT /directores/{id}
        url = `${API}/directores/${encodeURIComponent(idEditando)}`; 
        method = "PUT";
        
        // REGLA CRÍTICA: No enviar el ID en el cuerpo al editar para evitar Error 400
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
            // Extraemos el detalle del error para informar al usuario
            const error = await res.json();
            throw new Error(error.detail || "Error en el servidor");
        }
        return res.json();
    })
    .then(() => {
        alert(modoEdicion ? "Director actualizado exitosamente" : "Director creado exitosamente");
        cargarDirectores();
        cerrarModal();
    })
    .catch(err => alert("Error en la operación:\n" + err.message));
});

// 4. ELIMINACIÓN
function eliminarDirector(id) {
    if (!confirm(`¿Estás seguro de eliminar al director ${id}?`)) return;

    fetch(`${API}/directores/${encodeURIComponent(id)}`, { 
        method: "DELETE" 
    })
    .then(res => {
        if (res.ok) {
            alert("Director eliminado");
            cargarDirectores();
        } else {
            alert("Error al eliminar. Verifique si el director tiene escuelas asignadas.");
        }
    })
    .catch(err => alert("Failed to fetch: Error de red o CORS."));
}

// 5. GESTIÓN DE MODAL (Estándar de Oro)
function abrirModal() {
    const modal = document.getElementById("modalDirector");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open"); // Bloqueo de scroll
    }

    // Si entramos por el botón de "Nuevo", nos aseguramos de resetear el título
    if (!modoEdicion) {
        const title = document.getElementById("modalTitle");
        if (title) title.textContent = "Nuevo Director";
    }
}

function cerrarModal() {
    const modal = document.getElementById("modalDirector");
    if (modal) modal.style.display = "none";
    
    document.body.classList.remove("modal-open");
    document.getElementById("crearDirectorForm").reset();
    document.getElementById("id_unphu").disabled = false;
    
    // Reseteo de banderas de estado
    modoEdicion = false;
    idEditando = null;
}

// 6. CARGAR ESCUELAS (Fix: Usando plural 'escuelas')
function cargarEscuelas() {
    fetch(`${API}/escuelas/`) // Sincronizado con la base de datos pluralizada
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("codigo_escuela");
        if (!select) return;

        select.innerHTML = '<option value="">Ninguna / Por asignar</option>';
        const escuelas = Array.isArray(data) ? data : (data.escuelas || []);
        
        escuelas.forEach(e => {
            select.innerHTML += `<option value="${e.codigo}">${e.nombre}</option>`;
        });
    })
    .catch(err => console.error("Error cargando selector de escuelas:", err));
}

// INICIALIZACIÓN
document.addEventListener("DOMContentLoaded", () => {
    cargarDirectores();
    cargarEscuelas();
});

// Cerrar modal al hacer clic fuera del contenido
window.onclick = function(event) {
    const modal = document.getElementById("modalDirector");
    if (event.target == modal) cerrarModal();
}