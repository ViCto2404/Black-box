// Determinación de la URL de la API
const BASE_API_DIR = (typeof API_URL !== 'undefined') ? API_URL : "https://black-box-bryr.onrender.com";

let editandoId = null;

/**
 * Inicialización
 */
document.addEventListener("DOMContentLoaded", async () => {
    await Promise.all([
        cargarEscuelas(),
        listarDirectores()
    ]);

    document.getElementById("directorForm").addEventListener("submit", guardarDirector);
});

/**
 * Carga las escuelas para el selector del modal
 */
async function cargarEscuelas() {
    try {
        const response = await fetch(`${BASE_API_DIR}/escuelas/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const escuelas = await response.json();
        
        const select = document.getElementById("codigo_escuela");
        select.innerHTML = '<option value="">Seleccione Escuela</option>';

        escuelas.forEach(e => {
            const opt = document.createElement("option");
            opt.value = e.codigo;
            opt.textContent = `${e.codigo} - ${e.nombre}`;
            select.appendChild(opt);
        });
    } catch (error) {
        console.error("Error cargando escuelas:", error);
    }
}

/**
 * Lista todos los directores registrados
 */
async function listarDirectores() {
    try {
        const response = await fetch(`${BASE_API_DIR}/directores/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        
        const tbody = document.querySelector("#tablaDirectores tbody");
        tbody.innerHTML = "";

        data.forEach(d => {
            const tr = document.createElement("tr");
            const escuelaDisplay = d.nombre_escuela || d.codigo_escuela || 'Sin asignar';
            tr.innerHTML = `
                <td>${d.id_unphu}</td>
                <td>${d.nombre}</td>
                <td>${d.correo_institucional}</td>
                <td>${escuelaDisplay}</td>
                <td>
                    <button class="btn-editar" onclick="editarDirector('${d.id_unphu}')">✏️</button>
                    <button class="btn-eliminar" onclick="eliminarDirector('${d.id_unphu}')">🗑️</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Error listando directores:", error);
    }
}

/**
 * Guarda (Crea o Edita) un director
 */
async function guardarDirector(e) {
    e.preventDefault();
    
    const id_unphu = document.getElementById("id_unphu").value;
    const nombre = document.getElementById("nombre").value;
    const correo = document.getElementById("correo_institucional").value;
    const escuela = document.getElementById("codigo_escuela").value || null;

    const payload = {
        id_unphu: id_unphu,
        nombre: nombre,
        correo_institucional: correo,
        codigo_escuela: escuela
    };

    try {
        let response;
        if (editandoId) {
            // Edición
            response = await fetch(`${BASE_API_DIR}/directores/${editandoId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}` 
                },
                body: JSON.stringify({
                    nombre: nombre,
                    correo_institucional: correo,
                    codigo_escuela: escuela
                })
            });
        } else {
            // Creación
            response = await fetch(`${BASE_API_DIR}/directores/`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}` 
                },
                body: JSON.stringify(payload)
            });
        }

        if (response.ok) {
            alert("Director guardado correctamente");
            cerrarModal();
            listarDirectores();
        } else {
            const err = await response.json();
            alert("Error: " + (err.detail || "No se pudo guardar"));
        }
    } catch (error) {
        alert("Error de conexión");
    }
}

/**
 * Prepara el modal para editar
 */
async function editarDirector(id) {
    try {
        const response = await fetch(`${BASE_API_DIR}/directores/${id}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const d = await response.json();

        editandoId = id;
        document.getElementById("modalTitle").textContent = "Editar Director";
        
        document.getElementById("id_unphu").value = d.id_unphu;
        document.getElementById("id_unphu").disabled = true; // No se edita el ID primario
        document.getElementById("nombre").value = d.nombre;
        document.getElementById("correo_institucional").value = d.correo_institucional;
        document.getElementById("codigo_escuela").value = d.codigo_escuela || "";
        
        document.getElementById("modalDirector").style.display = "flex";
    } catch (error) {
        alert("Error al obtener datos del director");
    }
}

/**
 * Elimina un director
 */
async function eliminarDirector(id) {
    if (!confirm(`¿Está seguro de eliminar al director con ID ${id}?`)) return;

    try {
        const response = await fetch(`${BASE_API_DIR}/directores/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (response.ok) {
            listarDirectores();
        } else {
            alert("Error al eliminar");
        }
    } catch (error) {
        alert("Error de conexión");
    }
}

function abrirModal() {
    editandoId = null;
    document.getElementById("modalTitle").textContent = "Nuevo Director";
    document.getElementById("directorForm").reset();
    document.getElementById("id_unphu").disabled = false;
    document.getElementById("modalDirector").style.display = "flex";
}

function cerrarModal() {
    document.getElementById("modalDirector").style.display = "none";
}
