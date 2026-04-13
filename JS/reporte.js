/**
 * Funciones para el manejo de reportes ejecutivos con Modal Popover
 */

// Determinar la URL de la API de forma dinámica
let API_BASE_REPORTE = (typeof API_URL !== 'undefined') ? API_URL : "https://black-box-bryr.onrender.com";
if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    API_BASE_REPORTE = "http://127.0.0.1:8000";
}

/**
 * Maneja el cambio en el selector principal de reportes
 */
function manejarCambioReporte() {
    const tipo = document.getElementById("tipoReporte").value;
    if (tipo === "materia_detalle") {
        abrirModalMateria();
        // Resetear el selector para que el usuario pueda volver a elegir la misma opción si cierra el modal
        document.getElementById("tipoReporte").selectedIndex = 0;
    }
}

/**
 * Abre el modal y carga los datos necesarios
 */
async function abrirModalMateria() {
    document.getElementById("modalReporteMateria").style.display = "flex";
    await Promise.all([
        cargarMateriasModal(),
        cargarPeriodosModal()
    ]);
}

/**
 * Cierra el modal
 */
function cerrarModalMateria() {
    document.getElementById("modalReporteMateria").style.display = "none";
}

/**
 * Carga las materias filtrando por escuela si el usuario es director
 */
async function cargarMateriasModal() {
    const select = document.getElementById("modalMateriaSelect");
    const userRole = localStorage.getItem("userRole");
    const codigoEscuela = localStorage.getItem("codigoEscuela");

    try {
        let url = `${API_BASE_REPORTE}/materias/`;
        if (userRole === "director" && codigoEscuela) {
            url += `?codigo_escuela=${codigoEscuela}`;
        }
        
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        let materias = await response.json();

        // Si es director y tenemos el código de escuela, filtramos (asumiendo que tenemos acceso a la escuela de la materia)
        // Nota: Para un filtrado perfecto, el endpoint /materias/ debería aceptar codigo_escuela.
        if (userRole === "director" && codigoEscuela) {
            // Aquí se podría hacer una petición filtrada si el API lo soporta:
            // url = `${API_BASE_REPORTE}/materias/?codigo_escuela=${codigoEscuela}`;
            // Por ahora, si no hay filtro en API, mostramos las que correspondan si el objeto materia trae la info.
        }

        select.innerHTML = '<option value="">Seleccione una materia...</option>';
        materias.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m.codigo;
            opt.textContent = `${m.codigo} - ${m.nombre}`;
            select.appendChild(opt);
        });
    } catch (error) {
        console.error("Error cargando materias:", error);
        select.innerHTML = '<option value="">Error al cargar materias</option>';
    }
}

/**
 * Carga los periodos académicos disponibles
 */
async function cargarPeriodosModal() {
    const select = document.getElementById("modalPeriodoSelect");
    try {
        const response = await fetch(`${API_BASE_REPORTE}/dashboard/periodos`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const periodos = await response.json();

        select.innerHTML = '<option value="">Seleccione un periodo...</option>';
        periodos.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p;
            opt.textContent = p;
            select.appendChild(opt);
        });
    } catch (error) {
        console.error("Error cargando periodos:", error);
        select.innerHTML = '<option value="">Error al cargar periodos</option>';
    }
}

/**
 * Inicia la descarga desde el modal
 */
async function confirmarDescargaMateria() {
    const codigoMateria = document.getElementById("modalMateriaSelect").value;
    const periodo = document.getElementById("modalPeriodoSelect").value;
    const formato = document.getElementById("modalFormatoSelect").value;

    if (!codigoMateria || !periodo) {
        alert("Por favor seleccione materia y periodo.");
        return;
    }

    const btn = document.querySelector(".btn-confirm");
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = "⌛ Generando...";

    const usuarioActual = localStorage.getItem("id_unphu") || localStorage.getItem("username") || "ADMIN---UNPHU";
    const codigoEscuela = localStorage.getItem("codigoEscuela") || "";

    try {
        let endpoint = `/reportes/materia/${codigoMateria}/${periodo}?format=${formato}&usuario_actual=${usuarioActual}`;
        if (codigoEscuela) endpoint += `&codigo_escuela=${codigoEscuela}`;

        const nombreArchivo = `Analisis_Materia_${codigoMateria}_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;

        const response = await fetch(`${API_BASE_REPORTE}${endpoint}`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (!response.ok) throw new Error("Error al generar el reporte");

        const blob = await response.blob();
        const urlDescarga = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = urlDescarga;
        a.download = nombreArchivo;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(urlDescarga);
        
        cerrarModalMateria();
    } catch (error) {
        alert("No se pudo descargar el reporte: " + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

/**
 * Función original para los reportes directos del dashboard
 */
async function descargarReporte() {
    const anio = document.getElementById("filtroAnio")?.value;
    const cuatri = document.getElementById("filtroPeriodoCuatri")?.value;
    const tipoReporte = document.getElementById("tipoReporte").value;
    const formatoSelector = document.getElementById("formatoReporte");
    const formato = formatoSelector.value;

    if (tipoReporte === "materia_detalle") return; // Manejado por modal

    if (!anio || !cuatri) {
        alert("Por favor seleccione un periodo válido en los filtros del dashboard.");
        formatoSelector.selectedIndex = 0;
        return;
    }
    
    const periodo = `${cuatri}-${anio}`;
    const usuarioActual = localStorage.getItem("id_unphu") || localStorage.getItem("username") || "ADMIN---UNPHU";
    const codigoEscuela = localStorage.getItem("codigoEscuela") || "";

    try {
        let endpoint = "";
        let nombreArchivo = "";
        let extraParams = `format=${formato}&usuario_actual=${usuarioActual}`;
        
        if (codigoEscuela) {
            extraParams += `&codigo_escuela=${codigoEscuela}`;
        }

        if (tipoReporte === "resumen") {
            endpoint = `/reportes/resumen/${periodo}?${extraParams}`;
            nombreArchivo = `Resumen_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        } else if (tipoReporte === "rendimiento") {
            endpoint = `/reportes/rendimiento/${periodo}?${extraParams}`;
            nombreArchivo = `Rendimiento_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        } else if (tipoReporte === "criticas") {
            endpoint = `/reportes/criticas/${periodo}?${extraParams}`;
            nombreArchivo = `Materias_Criticas_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        } else if (tipoReporte === "feedback") {
            endpoint = `/reportes/feedback?${extraParams}`;
            nombreArchivo = `Feedback.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        }

        const response = await fetch(`${API_BASE_REPORTE}${endpoint}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });

        if (!response.ok) throw new Error("Error al generar el archivo");

        const blob = await response.blob();
        const urlDescarga = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = urlDescarga;
        a.download = nombreArchivo;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        formatoSelector.disabled = false;
        formatoSelector.options[0].text = originalText;
        formatoSelector.selectedIndex = 0;
    }
}
