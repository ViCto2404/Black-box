// Determinación de la URL de la API
let BASE_API_CALIF = (typeof API_URL !== 'undefined') ? API_URL : "https://black-box-bryr.onrender.com";
if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    BASE_API_CALIF = "http://127.0.0.1:8000";
}

let editandoId = null;

/**
 * Inicialización
 */
document.addEventListener("DOMContentLoaded", async () => {
    await Promise.all([
        cargarPeriodosFiltro(),
        cargarMateriasFiltro(),
        listarCalificaciones()
    ]);

    document.getElementById("calificacionForm").addEventListener("submit", guardarCalificacion);
});

/**
 * Carga los periodos para los FILTROS generales
 */
async function cargarPeriodosFiltro() {
    try {
        const response = await fetch(`${BASE_API_CALIF}/dashboard/periodos`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const periodos = await response.json();
        const filterSelect = document.getElementById("filtroPeriodo");
        
        filterSelect.innerHTML = '<option value="">Todos los periodos</option>';
        periodos.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p;
            opt.textContent = p;
            filterSelect.appendChild(opt);
        });
    } catch (error) {
        console.error("Error cargando periodos filtro:", error);
    }
}

/**
 * Carga las materias para los selectores (filtros y modal)
 */
async function cargarMateriasFiltro() {
    try {
        const response = await fetch(`${BASE_API_CALIF}/materias/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const materias = await response.json();
        
        const filterSelect = document.getElementById("filtroMateria");
        const modalSelect = document.getElementById("codigo_materia");

        materias.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m.codigo;
            opt.textContent = `${m.codigo} - ${m.nombre}`;
            filterSelect.appendChild(opt.cloneNode(true));
            modalSelect.appendChild(opt);
        });
    } catch (error) {
        console.error("Error cargando materias:", error);
    }
}

/**
 * [MODAL] Paso 1: Al elegir materia, cargar sus periodos disponibles
 */
async function cargarPeriodosPorMateria() {
    const codigoMateria = document.getElementById("codigo_materia").value;
    const periodoSelect = document.getElementById("periodo_academico");
    const seccionSelect = document.getElementById("id_seccion");

    // Reset dependientes
    periodoSelect.innerHTML = '<option value="">Cargando periodos...</option>';
    seccionSelect.innerHTML = '<option value="">Seleccione un periodo primero</option>';

    if (!codigoMateria) {
        periodoSelect.innerHTML = '<option value="">Seleccione una materia primero</option>';
        return;
    }

    try {
        // Consultamos todas las secciones de esa materia para ver qué periodos existen
        const response = await fetch(`${BASE_API_CALIF}/secciones/?materia=${codigoMateria}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const secciones = await response.json();
        
        // Extraer periodos únicos
        const periodosUnicos = [...new Set(secciones.map(s => s.periodo))].sort().reverse();

        periodoSelect.innerHTML = '<option value="">Seleccione periodo</option>';
        if (periodosUnicos.length === 0) {
            periodoSelect.innerHTML = '<option value="">No hay periodos registrados</option>';
        }

        periodosUnicos.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p;
            opt.textContent = p;
            periodoSelect.appendChild(opt);
        });
    } catch (error) {
        console.error("Error cargando periodos por materia:", error);
        periodoSelect.innerHTML = '<option value="">Error al cargar</option>';
    }
}

/**
 * [MODAL] Paso 2: Al elegir periodo, cargar las secciones exactas
 */
async function cargarSeccionesPorMateriaYPeriodo() {
    const codigoMateria = document.getElementById("codigo_materia").value;
    const periodo = document.getElementById("periodo_academico").value;
    const seccionSelect = document.getElementById("id_seccion");

    seccionSelect.innerHTML = '<option value="">Cargando secciones...</option>';

    if (!codigoMateria || !periodo) {
        seccionSelect.innerHTML = '<option value="">Seleccione periodo primero</option>';
        return;
    }

    try {
        const response = await fetch(`${BASE_API_CALIF}/secciones/?materia=${codigoMateria}&periodo=${periodo}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const secciones = await response.json();
        
        seccionSelect.innerHTML = '<option value="">Seleccione sección</option>';
        secciones.forEach(s => {
            const opt = document.createElement("option");
            opt.value = s.id; 
            opt.textContent = `${s.codigo_seccion} - ${s.horario || 'S/H'}`;
            seccionSelect.appendChild(opt);
        });
    } catch (error) {
        console.error("Error cargando secciones filtradas:", error);
        seccionSelect.innerHTML = '<option value="">Error al cargar</option>';
    }
}

/**
 * Lista las calificaciones con los filtros aplicados
 */
async function listarCalificaciones() {
    const periodo = document.getElementById("filtroPeriodo").value;
    const materia = document.getElementById("filtroMateria").value;
    const estudiante = document.getElementById("filtroEstudiante").value;

    let url = `${BASE_API_CALIF}/calificaciones/?`;
    if (periodo) url += `periodo=${periodo}&`;
    if (materia) url += `codigo_materia=${materia}&`;
    if (estudiante) url += `id_estudiante=${estudiante}&`;

    try {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        
        const tbody = document.querySelector("#tablaCalificaciones tbody");
        tbody.innerHTML = "";

        data.forEach(c => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${c.id_estudiante}</td>
                <td>${c.codigo_materia}</td>
                <td>${c.id_seccion}</td>
                <td>${c.periodo_academico}</td>
                <td style="font-weight: bold; color: ${c.nota >= 70 ? '#1a5c2e' : '#c0392b'}">${c.nota}</td>
                <td>
                    <button class="btn-edit" onclick="editarCalificacion(${c.id}, ${c.nota})">✏️</button>
                    <button class="btn-delete" onclick="eliminarCalificacion(${c.id})">🗑️</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Error listando calificaciones:", error);
    }
}

/**
 * Guarda (Crea o Edita) una calificación
 */
async function guardarCalificacion(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData.entries());
    payload.nota = parseFloat(payload.nota);
    payload.id_seccion = parseInt(payload.id_seccion);

    try {
        let response;
        if (editandoId) {
            response = await fetch(`${BASE_API_CALIF}/calificaciones/${editandoId}/nota?nota=${payload.nota}`, {
                method: 'PATCH',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
        } else {
            response = await fetch(`${BASE_API_CALIF}/calificaciones/`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}` 
                },
                body: JSON.stringify(payload)
            });
        }

        if (response.ok) {
            alert("Calificación guardada correctamente");
            cerrarModal();
            listarCalificaciones();
        } else {
            const err = await response.json();
            alert("Error: " + (err.detail || "No se pudo guardar"));
        }
    } catch (error) {
        alert("Error de conexión");
    }
}

/**
 * Prepara el modal para editar (Limitado a cambiar nota según API)
 */
function editarCalificacion(id, notaActual) {
    editandoId = id;
    document.getElementById("modalTitle").textContent = "Editar Nota";
    
    document.getElementById("id_estudiante").disabled = true;
    document.getElementById("codigo_materia").disabled = true;
    document.getElementById("id_seccion").disabled = true;
    document.getElementById("periodo_academico").disabled = true;
    
    document.getElementById("nota").value = notaActual;
    document.getElementById("modalCalificacion").style.display = "block";
}

/**
 * Elimina una calificación
 */
async function eliminarCalificacion(id) {
    if (!confirm("¿Está seguro de eliminar esta calificación?")) return;

    try {
        const response = await fetch(`${BASE_API_CALIF}/calificaciones/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (response.ok) {
            listarCalificaciones();
        } else {
            alert("Error al eliminar");
        }
    } catch (error) {
        alert("Error de conexión");
    }
}

function abrirModal() {
    editandoId = null;
    document.getElementById("modalTitle").textContent = "Nueva Calificación";
    document.getElementById("calificacionForm").reset();
    
    document.getElementById("id_estudiante").disabled = false;
    document.getElementById("codigo_materia").disabled = false;
    document.getElementById("id_seccion").disabled = false;
    document.getElementById("periodo_academico").disabled = false;
    
    document.getElementById("modalCalificacion").style.display = "block";
}

function cerrarModal() {
    document.getElementById("modalCalificacion").style.display = "none";
}
