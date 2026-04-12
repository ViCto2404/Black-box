const API = "https://black-box-bryr.onrender.com";
let modoEdicion = false;
let idEditando = null; 
let contadorHorarios = 0;

// --- GESTIÓN DE INTERFAZ ---

function abrirModal() {
    const modal = document.getElementById("modalSeccion");
    if (modal) {
        modal.style.display = "flex";
        document.body.classList.add("modal-open");
    }

    if (!modoEdicion) {
        document.getElementById("modalTitle").textContent = "Nueva Sección";
        const contenedor = document.getElementById("contenedorHorarios");
        if (contenedor) contenedor.innerHTML = "";
        contadorHorarios = 0;
        agregarHorario(); 
    }
}

function cerrarModal() {
    const modal = document.getElementById("modalSeccion");
    if (modal) modal.style.display = "none";
    
    document.body.classList.remove("modal-open");
    document.getElementById("crearSeccionForm").reset();
    document.getElementById("contenedorHorarios").innerHTML = "";
    document.getElementById("codigoSeccion").disabled = false;
    document.getElementById("materiaSeccion").disabled = false;

    modoEdicion = false;
    idEditando = null;
}

window.onclick = function(event) {
    if (event.target == document.getElementById("modalSeccion")) cerrarModal();
}

// --- LÓGICA DE HORARIOS ---

function agregarHorario(datosPrevios = null) {
    if (contadorHorarios >= 3) {
        alert("Máximo 3 horarios permitidos.");
        return;
    }

    contadorHorarios++;
    const contenedor = document.getElementById("contenedorHorarios");
    const div = document.createElement("div");
    div.className = "schedule-group";
    div.id = `grupo-horario-${contadorHorarios}`;
    div.style.marginBottom = "10px";
    div.style.display = "flex";
    div.style.gap = "8px";
    
    div.innerHTML = `
        <select name="diaSemana" required style="flex: 1.5;">
            <option value="">Día</option>
            <option value="Lunes">Lunes</option>
            <option value="Martes">Martes</option>
            <option value="Miercoles">Miércoles</option>
            <option value="Jueves">Jueves</option>
            <option value="Viernes">Viernes</option>
            <option value="Sabado">Sábado</option>
        </select>
        <input type="time" name="horaInicio" required style="flex: 1;">
        <input type="time" name="horaFin" required style="flex: 1;">
        <button type="button" onclick="eliminarFilaHorario(${contadorHorarios})" 
                style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
            ×
        </button>
    `;

    contenedor.appendChild(div);

    if (datosPrevios) {
        try {
            const partes = datosPrevios.split(" ");
            const horas = partes[1].split("-");
            div.querySelector('select[name="diaSemana"]').value = partes[0];
            div.querySelector('input[name="horaInicio"]').value = horas[0];
            div.querySelector('input[name="horaFin"]').value = horas[1];
        } catch (e) { console.error("Error horario:", e); }
    }
}

function eliminarFilaHorario(id) {
    const fila = document.getElementById(`grupo-horario-${id}`);
    if (fila) {
        fila.remove();
        contadorHorarios--;
    }
}

// --- CRUD ---

function cargarSecciones() {
    fetch(`${API}/secciones`)
    .then(res => res.json())
    .then(data => {
        const tabla = document.querySelector("#tablaSecciones tbody");
        if (!tabla) return;
        tabla.innerHTML = "";
        const secciones = data.secciones || data.data || data;

        secciones.forEach(s => {
            tabla.innerHTML += `
            <tr>
                <td>${s.codigo_seccion}</td>
                <td>${s.materia}</td>
                <td>${s.profesor || "No asignado"}</td>
                <td>${s.aula || "N/A"}</td>
                <td class="${s.estado === 'Activa' ? 'estado-activa' : 'estado-inactiva'}">
                    ${s.estado}
                </td>
                <td>
                    <button class="btn-editar" onclick="editarSeccion(${s.id})">Editar</button>
                    <button class="btn-eliminar" onclick="eliminarSeccion(${s.id})">Eliminar</button>
                </td>
            </tr>`;
        });
    });
}

function cargarMateriasYProfesores() {
    fetch(`${API}/materias`).then(res => res.json()).then(data => {
        const select = document.getElementById("materiaSeccion");
        const materias = data.materias || data.data || data;
        materias.forEach(m => select.innerHTML += `<option value="${m.codigo}">${m.nombre}</option>`);
    });

    fetch(`${API}/profesores`).then(res => res.json()).then(data => {
        const select = document.getElementById("profesorSeccion");
        const profesores = data.profesores || data.data || data;
        profesores.forEach(p => select.innerHTML += `<option value="${p.id_profesor}">${p.nombre}</option>`);
    });
}

function editarSeccion(id) {
    fetch(`${API}/secciones/${id}`)
    .then(res => res.json())
    .then(s => {
        document.getElementById("codigoSeccion").value = s.codigo_seccion;
        document.getElementById("materiaSeccion").value = s.materia;
        document.getElementById("profesorSeccion").value = s.profesor;
        document.getElementById("aula").value = s.aula;
        document.getElementById("cupoSeccion").value = s.cupo_max;
        document.getElementById("estadoSeccion").value = s.estado;

        document.getElementById("contenedorHorarios").innerHTML = "";
        contadorHorarios = 0;
        if (s.horario) s.horario.split(", ").forEach(h => agregarHorario(h));

        document.getElementById("codigoSeccion").disabled = true;
        document.getElementById("materiaSeccion").disabled = true;
        document.getElementById("modalTitle").textContent = "Editar Sección";
        
        modoEdicion = true;
        idEditando = id;
        abrirModal();
    });
}

function eliminarSeccion(id) {
    if (!confirm("¿Eliminar esta sección?")) return;
    fetch(`${API}/secciones/${id}`, { method: "DELETE" })
    .then(res => {
        if (res.ok) { alert("Sección eliminada"); cargarSecciones(); }
    });
}

document.getElementById("crearSeccionForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const listaHorarios = [];
    document.querySelectorAll(".schedule-group").forEach(grupo => {
        const d = grupo.querySelector('[name="diaSemana"]').value;
        const i = grupo.querySelector('[name="horaInicio"]').value;
        const f = grupo.querySelector('[name="horaFin"]').value;
        if(d && i && f) listaHorarios.push(`${d} ${i}-${f}`);
    });

    // --- EL TRUCO PARA EVITAR EL ERROR 400 ---
    let data;
    if (modoEdicion) {
        // Solo enviamos los campos permitidos en SeccionUpdate
        data = {
            profesor: document.getElementById("profesorSeccion").value,
            aula: document.getElementById("aula").value,
            cupo_max: parseInt(document.getElementById("cupoSeccion").value),
            horario: listaHorarios.join(", "),
            estado: document.getElementById("estadoSeccion").value
        };
    } else {
        // Enviamos todo lo que pide SeccionCreate
        data = {
            codigo_seccion: document.getElementById("codigoSeccion").value,
            materia: document.getElementById("materiaSeccion").value,
            profesor: document.getElementById("profesorSeccion").value,
            periodo: "01-2026", 
            aula: document.getElementById("aula").value,
            cupo_max: parseInt(document.getElementById("cupoSeccion").value),
            horario: listaHorarios.join(", "),
            estado: document.getElementById("estadoSeccion").value
        };
    }

    let url = modoEdicion ? `${API}/secciones/${idEditando}` : `${API}/secciones`;
    let method = modoEdicion ? "PUT" : "POST";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(async res => {
        if (res.ok) return res.json();
        const err = await res.json();
        throw new Error(err.detail || "Error en el servidor");
    })
    .then(() => {
        alert(modoEdicion ? "Sección actualizada" : "Sección creada");
        cargarSecciones();
        cerrarModal();
    })
    .catch(err => alert("Error 400: " + err.message));
});

document.addEventListener("DOMContentLoaded", () => {
    cargarSecciones();
    cargarMateriasYProfesores();
});