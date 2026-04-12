// Usamos API_URL de config.js
let modoEdicion = false;
let idEditando = null;

// --- GESTIÓN DE INTERFAZ ---

function abrirModal() {
    const modal = document.getElementById("modalEstudiante");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
    }
    if (!modoEdicion) {
        document.getElementById("modalTitle").textContent = "Nuevo Estudiante";
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

window.onclick = function(event) {
    const modal = document.getElementById("modalEstudiante");
    if (event.target == modal) cerrarModal();
}

// --- CARGA DE DATOS ---

function cargarEstudiantes() {
    fetch(`${API_URL}/estudiantes`)
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaEstudiantes tbody");
        if (!tabla) return;
        tabla.innerHTML = "";
        
        const estudiantes = data.estudiantes || data.data || data;

        estudiantes.forEach(est => {
            tabla.innerHTML += `
            <tr>
                <td>${est.id_unphu}</td>
                <td>${est.nombre}</td>
                <td>${est.nombre_carrera || est.codigo_carrera}</td>
                <td>${est.correo_institucional || "N/A"}</td>
                <td class="${est.estado_activo === 'Activo' ? 'estado-activa' : 'estado-inactiva'}">
                    ${est.estado_activo}
                </td>
                <td>
                    <button class="btn-editar" onclick="editarEstudiante('${est.id_unphu}')">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarEstudiante('${est.id_unphu}')">Eliminar</button>
                </td>
            </tr>`;
        });
    });
}

function cargarCarreras() {
    fetch(`${API_URL}/carreras`)
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("carrera");
        if (!select) return;
        select.innerHTML = '<option value="">Seleccione una carrera</option>';
        const carreras = data.carreras || data.data || data;
        carreras.forEach(c => {
            select.innerHTML += `<option value="${c.codigo}">${c.nombre}</option>`;
        });
    });
}

// --- OPERACIONES CRUD ---

function editarEstudiante(id_unphu) {
    fetch(`${API_URL}/estudiantes/${id_unphu}`)
    .then(res => res.json())
    .then(est => {
        document.getElementById("id_unphu").value = est.id_unphu;
        document.getElementById("nombre").value = est.nombre;
        document.getElementById("carrera").value = est.codigo_carrera;
        document.getElementById("correo").value = est.correo_institucional || "";
        document.getElementById("estado").value = est.estado_activo;

        document.getElementById("id_unphu").disabled = true;
        document.getElementById("modalTitle").textContent = "Editar Estudiante";
        
        modoEdicion = true;
        idEditando = id_unphu;
        abrirModal();
    });
}

function eliminarEstudiante(id_unphu) {
    if (!confirm(`¿Eliminar al estudiante ${id_unphu}?`)) return;

    fetch(`${API_URL}/estudiantes/${id_unphu}`, { method: "DELETE" })
    .then(async res => {
        if (res.ok) {
            alert("Estudiante eliminado");
            cargarEstudiantes();
        } else {
            const err = await res.json();
            throw new Error(err.detail || "Error al eliminar");
        }
    })
    .catch(error => alert("Error: " + error.message));
}

// --- FORM SUBMIT (POST / PATCH) ---

document.getElementById("crearEstudianteForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const id_unphu = document.getElementById("id_unphu").value;
    const nombre = document.getElementById("nombre").value;
    const carrera = document.getElementById("carrera").value;
    const correo = document.getElementById("correo").value;
    const estado = document.getElementById("estado").value;

    let data = {
        nombre: nombre,
        codigo_carrera: carrera,
        correo_institucional: correo,
        estado_activo: estado
    };

    let url = `${API_URL}/estudiantes`;
    let method = "POST";

    if (modoEdicion) {
        url = `${API_URL}/estudiantes/${idEditando}`;
        method = "PATCH"; // Tu API de estudiantes usa PATCH para actualizar
    } else {
        data.id_unphu = id_unphu;
    }

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(async res => {
        if (res.ok) return res.json();
        const err = await res.json();
        throw new Error(err.detail || "Error al procesar la solicitud");
    })
    .then(() => {
        alert(modoEdicion ? "Estudiante actualizado" : "Estudiante creado");
        cargarEstudiantes();
        cerrarModal();
    })
    .catch(err => alert("Error: " + err.message));
});

document.addEventListener("DOMContentLoaded", () => {
    cargarEstudiantes();
    cargarCarreras();
});
