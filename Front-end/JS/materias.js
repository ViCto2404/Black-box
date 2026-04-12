// Usamos API_URL de config.js
let modoEdicion = false;
let codigoEditando = null;

// --- GESTIÓN DE INTERFAZ ---

function abrirModal() {
    const modal = document.getElementById("modalMateria");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
    }
    if (!modoEdicion) {
        document.getElementById("modalTitle").textContent = "Nueva Materia";
    }
}

function cerrarModal() {
    const modal = document.getElementById("modalMateria");
    if (modal) modal.style.display = "none";
    
    document.body.classList.remove("modal-open");
    document.getElementById("crearMateriaForm").reset();
    document.getElementById("codigo").disabled = false;

    modoEdicion = false;
    codigoEditando = null;
}

window.onclick = function(event) {
    const modal = document.getElementById("modalMateria");
    if (event.target == modal) cerrarModal();
}

// --- CARGA DE DATOS ---

function cargarMaterias() {
    fetch(`${API_URL}/materias`)
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaMaterias tbody");
        if (!tabla) return;
        tabla.innerHTML = "";
        
        const materias = data.materias || data.data || data;

        materias.forEach(m => {
            tabla.innerHTML += `
            <tr>
                <td>${m.codigo}</td>
                <td>${m.nombre}</td>
                <td>${m.codigo_carrera}</td>
                <td>${m.creditos}</td>
                <td>${m.cupo_maximo}</td>
                <td class="${m.estado === 'Activa' ? 'estado-activa' : 'estado-inactiva'}">
                    ${m.estado}
                </td>
                <td>
                    <button class="btn-editar" onclick="editarMateria('${m.codigo}')">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarMateria('${m.codigo}')">Eliminar</button>
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

function cargarProfesores() {
    fetch(`${API_URL}/profesores`)
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("profesor");
        if (!select) return;
        select.innerHTML = '<option value="">Seleccione un profesor (Opcional)</option>';
        const profesores = data.profesores || data.data || data;
        profesores.forEach(p => {
            select.innerHTML += `<option value="${p.id_profesor}">${p.nombre}</option>`;
        });
    });
}

// --- OPERACIONES CRUD ---

function editarMateria(codigo) {
    fetch(`${API_URL}/materias/${codigo}`)
    .then(res => res.json())
    .then(m => {
        document.getElementById("codigo").value = m.codigo;
        document.getElementById("nombre").value = m.nombre;
        document.getElementById("carrera").value = m.codigo_carrera;
        document.getElementById("creditos").value = m.creditos;
        document.getElementById("profesor").value = m.id_profesor || "";
        document.getElementById("cupo").value = m.cupo_maximo;
        document.getElementById("estado").value = m.estado;

        document.getElementById("codigo").disabled = true;
        document.getElementById("modalTitle").textContent = "Editar Materia";
        
        modoEdicion = true;
        codigoEditando = codigo;
        abrirModal();
    });
}

function eliminarMateria(codigo) {
    if (!confirm(`¿Eliminar la materia ${codigo}?`)) return;

    fetch(`${API_URL}/materias/${codigo}`, { method: "DELETE" })
    .then(async res => {
        if (res.ok) {
            alert("Materia eliminada");
            cargarMaterias();
        } else {
            const err = await res.json();
            throw new Error(err.detail || "Error al eliminar");
        }
    })
    .catch(error => alert("Error: " + error.message));
}

// --- FORM SUBMIT (POST / PUT) ---

document.getElementById("crearMateriaForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const nombre = document.getElementById("nombre").value;
    const carrera = document.getElementById("carrera").value;
    const creditos = parseInt(document.getElementById("creditos").value);
    const profesorInput = document.getElementById("profesor").value;
    const profesor = profesorInput === "" ? null : profesorInput;
    const cupo = parseInt(document.getElementById("cupo").value);
    const estado = document.getElementById("estado").value;

    let data = {
        nombre: nombre,
        codigo_carrera: carrera,
        creditos: creditos,
        id_profesor: profesor,
        cupo_maximo: cupo,
        estado: estado
    };

    if (!modoEdicion) {
        data.codigo = document.getElementById("codigo").value;
    }

    let url = modoEdicion ? `${API_URL}/materias/${codigoEditando}` : `${API_URL}/materias`;
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
        alert(modoEdicion ? "Materia actualizada" : "Materia creada");
        cargarMaterias();
        cerrarModal();
    })
    .catch(err => alert("Error: " + err.message));
});

document.addEventListener("DOMContentLoaded", () => {
    cargarMaterias();
    cargarCarreras();
    cargarProfesores();
});
