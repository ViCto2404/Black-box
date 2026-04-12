const API = "https://black-box-bryr.onrender.com";

let modoEdicion = false;
let idEditando = null;

function abrirModal() {
    const modal = document.getElementById("modalProfesor");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
    }

    if (!modoEdicion) {
        const title = document.getElementById("modalTitle");
        if (title) title.textContent = "Nuevo Profesor";
    }
}

function cerrarModal() {
    const modal = document.getElementById("modalProfesor");
    if (modal) modal.style.display = "none";
    
    document.body.classList.remove("modal-open");
    document.getElementById("crearProfesorForm").reset();
    document.getElementById("idProfesor").disabled = false;

    modoEdicion = false;
    idEditando = null;
}

window.onclick = function(event) {
    if (event.target == document.getElementById("modalProfesor")) cerrarModal();
}

function cargarProfesores() {
    fetch(API + "/profesores/")
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaProfesores tbody");
        tabla.innerHTML = "";
        const profesores = data.profesores || data.data || data;

        profesores.forEach(p => {
            tabla.innerHTML += `
            <tr>
                <td>${p.id_profesor}</td>
                <td>${p.nombre}</td>
                <td>${p.correo_institucional}</td>
                <td>${p.codigo_carrera?.nombre || p.codigo_carrera || "N/A"}</td>
                <td class="${p.estado === 'Activo' ? 'estado-activa' : 'estado-inactiva'}">
                    ${p.estado}
                </td>
                <td>
                    <button class="btn-editar" onclick="editarProfesor('${p.id_profesor}')">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarProfesor('${p.id_profesor}')">Eliminar</button>
                </td>
            </tr>`;
        });
    });
}

function cargarCarreras() {
    fetch(API + "/carreras/")
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("carreraProfesor");
        select.innerHTML = '<option value="">Seleccione Carrera</option>';
        const carreras = data.carreras || data.data || data;
        carreras.forEach(c => {
            select.innerHTML += `<option value="${c.codigo}">${c.nombre}</option>`;
        });
    })
    .catch(err => console.error("Error cargando carreras:", err));
}

function editarProfesor(id) {
    fetch(API + "/profesores/" + id)
    .then(res => res.json())
    .then(p => {
        document.getElementById("idProfesor").value = p.id_profesor;
        document.getElementById("nombreProfesor").value = p.nombre;
        document.getElementById("correoProfesor").value = p.correo_institucional;
        document.getElementById("carreraProfesor").value = p.codigo_carrera;
        document.getElementById("estadoProfesor").value = p.estado;

        document.getElementById("idProfesor").disabled = true;
        document.getElementById("modalTitle").textContent = "Editar Profesor";

        modoEdicion = true;
        idEditando = id;
        abrirModal();
    });
}

function eliminarProfesor(id) {
    if (!confirm("¿Eliminar profesor " + id + "?")) return;
    fetch(API + "/profesores/" + id, { method: "DELETE" })
    .then(res => {
        if (res.ok) {
            alert("Profesor eliminado");
            cargarProfesores();
        }
    });
}

document.getElementById("crearProfesorForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const data = {
        id_profesor: document.getElementById("idProfesor").value,
        nombre: document.getElementById("nombreProfesor").value,
        correo_institucional: document.getElementById("correoProfesor").value,
        codigo_carrera: document.getElementById("carreraProfesor").value,
        estado: document.getElementById("estadoProfesor").value
    };

    let url = API + "/profesores/";
    let method = "POST";
    if (modoEdicion) {
        url = API + "/profesores/" + idEditando;
        method = "PUT";
    }

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => {
        if (!res.ok) throw new Error("Error al guardar");
        return res.json();
    })
    .then(() => {
        alert(modoEdicion ? "Profesor actualizado" : "Profesor creado");
        cargarProfesores();
        cerrarModal();
    })
    .catch(err => alert(err));
});

document.addEventListener("DOMContentLoaded", () => {
    cargarProfesores();
    cargarCarreras();
});