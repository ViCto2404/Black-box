// Usamos API_URL de config.js
let modoEdicion = false;
let idEditando = null;

// --- GESTIÓN DE MODAL ---

function abrirModal() {
    const modal = document.getElementById("modalEscuela");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
    }
    if (!modoEdicion) {
        const title = document.getElementById("modalTitle");
        if (title) title.textContent = "Nueva Escuela";
    }
}

function cerrarModal() {
    const modal = document.getElementById("modalEscuela");
    if (modal) modal.style.display = "none";
    
    document.body.classList.remove("modal-open");
    document.getElementById("crearEscuelaForm").reset();
    document.getElementById("codigoEscuela").disabled = false;
    
    modoEdicion = false;
    idEditando = null;
}

window.onclick = function(event) {
    const modal = document.getElementById("modalEscuela");
    if (event.target == modal) cerrarModal();
}

// --- CARGA DE DATOS ---

function cargarEscuelas() {
    fetch(`${API_URL}/escuelas`)
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaEscuelas tbody");
        if (!tabla) return;
        tabla.innerHTML = "";
        
        const escuelas = data.escuelas || data.data || data;

        escuelas.forEach(e => {
            const nombreDirector = e.id_director?.nombre || e.id_director || "Sin Director";
            
            tabla.innerHTML += `
            <tr>
                <td>${e.codigo}</td>
                <td>${e.nombre}</td>
                <td>${nombreDirector}</td>
                <td class="${e.estado === 'Activa' ? 'estado-activa' : 'estado-inactiva'}">
                    ${e.estado}
                </td>
                <td>
                    <button class="btn-editar" onclick="editarEscuela('${e.codigo}')">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarEscuela('${e.codigo}')">Eliminar</button>
                </td>
            </tr>`;
        });
    });
}

function cargarDirectores() {
    // Usamos el endpoint de directores tal como se solicitó
    fetch(`${API_URL}/directores`)
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("directorEscuela");
        if (!select) return;
        select.innerHTML = '<option value="">Seleccione un director</option>';
        
        // Manejamos la respuesta según el formato de la API
        const directores = data.directores || data.data || data;
        directores.forEach(d => {
            // Se muestra ID y Nombre en el selector
            select.innerHTML += `<option value="${d.id_unphu}">${d.id_unphu} - ${d.nombre}</option>`;
        });
    })
    .catch(err => console.error("Error al cargar directores:", err));
}

// --- OPERACIONES CRUD ---

function editarEscuela(codigo) {
    fetch(`${API_URL}/escuelas/${codigo}`)
    .then(res => res.json())
    .then(e => {
        document.getElementById("codigoEscuela").value = e.codigo;
        document.getElementById("nombreEscuela").value = e.nombre;
        document.getElementById("directorEscuela").value = e.id_director?.id_director || e.id_director;
        document.getElementById("estadoEscuela").value = e.estado;

        document.getElementById("codigoEscuela").disabled = true;
        document.getElementById("modalTitle").textContent = "Editar Escuela";

        modoEdicion = true;
        idEditando = codigo;
        abrirModal();
    });
}

function eliminarEscuela(codigo) {
    if (!confirm(`¿Eliminar escuela ${codigo}?`)) return;
    
    fetch(`${API_URL}/escuelas/${codigo}`, { method: "DELETE" })
    .then(res => {
        if (res.ok) {
            alert("Escuela eliminada");
            cargarEscuelas();
        } else {
            return res.json().then(err => { throw new Error(err.detail || "Error"); });
        }
    })
    .catch(err => alert("Error: " + err.message));
}

// --- SUBMIT DEL FORMULARIO ---

document.getElementById("crearEscuelaForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    let data;
    const nombre = document.getElementById("nombreEscuela").value;
    const director = document.getElementById("directorEscuela").value;
    const estado = document.getElementById("estadoEscuela").value;

    if (modoEdicion) {
        data = {
            nombre: nombre,
            id_director: director,
            estado: estado
        };
    } else {
        data = {
            codigo: document.getElementById("codigoEscuela").value,
            nombre: nombre,
            id_director: director,
            estado: estado
        };
    }

    let url = modoEdicion ? `${API_URL}/escuelas/${idEditando}` : `${API_URL}/escuelas`;
    let method = modoEdicion ? "PUT" : "POST";

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
        alert(modoEdicion ? "Escuela actualizada" : "Escuela creada");
        cargarEscuelas();
        cerrarModal();
    })
    .catch(err => alert("Error 400: " + err.message));
});

document.addEventListener("DOMContentLoaded", () => {
    cargarEscuelas();
    cargarDirectores();
});
