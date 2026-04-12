// Usamos API_URL de config.js

let modoEdicion = false;
let idEditando = null;

function abrirModal() {
    const modal = document.getElementById("modalCarrera");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
    }
    if (!modoEdicion) {
        const title = document.getElementById("modalTitle");
        if (title) title.textContent = "Nueva Carrera";
    }
}

function cerrarModal() {
    const modal = document.getElementById("modalCarrera");
    if (modal) modal.style.display = "none";
    
    document.body.classList.remove("modal-open");
    document.getElementById("crearCarreraForm").reset();
    document.getElementById("codigoCarrera").disabled = false;

    modoEdicion = false;
    idEditando = null;
}

window.onclick = function(event) {
    if (event.target == document.getElementById("modalCarrera")) cerrarModal();
}

// CARGAR LISTADO
function cargarCarreras() {
    fetch(`${API_URL}/carreras`)
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaCarreras tbody");
        if (!tabla) return;
        tabla.innerHTML = "";
        const carreras = data.carreras || data.data || data;

        carreras.forEach(c => {
            tabla.innerHTML += `
            <tr>
                <td>${c.codigo}</td>
                <td>${c.nombre}</td>
                <td>${c.codigo_escuela}</td>
                <td>${c.duracion_anos} años</td>
                <td class="${c.estado === 'Activa' ? 'estado-activa' : 'estado-inactiva'}">
                    ${c.estado}
                </td>
                <td>
                    <button class="btn-editar" onclick="editarCarrera('${c.codigo}')">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarCarrera('${c.codigo}')">Eliminar</button>
                </td>
            </tr>`;
        });
    });
}

// CARGAR SELECT DE ESCUELAS
function cargarEscuelas() {
    fetch(`${API_URL}/escuelas`)
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("escuelaCarrera");
        if (!select) return;
        select.innerHTML = '<option value="">Seleccione Escuela</option>';
        const escuelas = data.escuelas || data.data || data;
        escuelas.forEach(e => {
            select.innerHTML += `<option value="${e.codigo}">${e.nombre}</option>`;
        });
    })
    .catch(err => console.error("Error cargando escuelas:", err));
}

// EDITAR (Cargar datos al form)
function editarCarrera(codigo) {
    fetch(`${API_URL}/carreras/${codigo}`)
    .then(res => {
        if (!res.ok) throw new Error("No se pudo obtener la carrera");
        return res.json();
    })
    .then(c => {
        document.getElementById("codigoCarrera").value = c.codigo;
        document.getElementById("nombreCarrera").value = c.nombre;
        document.getElementById("escuelaCarrera").value = c.codigo_escuela;
        document.getElementById("duracion").value = c.duracion_anos;
        document.getElementById("estadoCarrera").value = c.estado;

        document.getElementById("codigoCarrera").disabled = true;
        document.getElementById("modalTitle").textContent = "Editar Carrera";
        
        modoEdicion = true;
        idEditando = codigo;
        abrirModal();
    })
    .catch(err => alert(err.message));
}

// ELIMINAR
function eliminarCarrera(codigo) {
    if (!confirm(`¿Estás seguro de eliminar la carrera ${codigo}?`)) return;

    fetch(`${API_URL}/carreras/${codigo}`, { 
        method: "DELETE" 
    })
    .then(async res => {
        if (res.ok) {
            alert("Carrera eliminada con éxito");
            cargarCarreras();
        } else {
            const errorData = await res.json();
            throw new Error(errorData.detail || "Error al eliminar");
        }
    })
    .catch(err => alert("Error 400: " + err.message));
}

// SUBMIT (CREAR / ACTUALIZAR)
document.getElementById("crearCarreraForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const data = {
        codigo: document.getElementById("codigoCarrera").value,
        nombre: document.getElementById("nombreCarrera").value,
        codigo_escuela: document.getElementById("escuelaCarrera").value,
        duracion_anos: parseInt(document.getElementById("duracion").value),
        estado: document.getElementById("estadoCarrera").value
    };

    let url = `${API_URL}/carreras`;
    let method = "POST";

    if (modoEdicion) {
        url = `${API_URL}/carreras/${idEditando}`;
        method = "PUT";
    }

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(async res => {
        if (res.ok) return res.json();
        
        // Si hay error 400 o 422, capturamos el mensaje de FastAPI
        const errorData = await res.json();
        throw new Error(errorData.detail || "Error en los datos");
    })
    .then(() => {
        alert(modoEdicion ? "Carrera actualizada" : "Carrera creada");
        cargarCarreras();
        cerrarModal();
    })
    .catch(err => alert("Error: " + err.message));
});

document.addEventListener("DOMContentLoaded", function() {
    cargarCarreras();
    cargarEscuelas();
});
