// Registrar el plugin de datalabels
Chart.register(ChartDataLabels);

let chartMasa, chartRendimiento;
let dashboardAbortController = null;
let reloadInProgress = false; // Guard para evitar bucles de recarga

// Determinar la URL de la API de forma dinámica
const BASE_API_DASH = (typeof API_URL !== 'undefined') ? API_URL : "https://black-box-bryr.onrender.com";

async function actualizarDashboard() {
    const periodo = document.getElementById("filtroPeriodoGlobal")?.value;
    const carreraSeleccionada = document.getElementById("filtroCarreraRendimiento")?.value || "";
    if (!periodo) return;

    console.log(`[Dashboard] Actualizando para Periodo: ${periodo}, Carrera: ${carreraSeleccionada}`);

    // 1. HARD RESET
    if (dashboardAbortController) dashboardAbortController.abort();
    dashboardAbortController = new AbortController();
    const signal = dashboardAbortController.signal;

    // Guardar estado para recuperación tras recarga
    sessionStorage.setItem("lastPeriodo", periodo);
    sessionStorage.setItem("lastCarrera", carreraSeleccionada);

    // Reset Visual
    document.querySelectorAll('.no-data-msg').forEach(m => m.remove());
    const allCards = document.querySelectorAll('.card, .card-chart');
    allCards.forEach(c => {
        c.style.opacity = '0.6';
        c.style.transition = 'opacity 0.3s ease';
    });

    const kpiIds = ["promedio", "tasaAprobacion", "totalEstudiantes", "materiasCriticas"];
    kpiIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = "...";
    });

    // VALIDACIÓN DE INTEGRIDAD ACTIVA
    const validarIntegridadVisual = (tipo, dataRecibida) => {
        if (reloadInProgress) return;

        setTimeout(() => {
            let errorDetectado = false;
            let motivo = "";

            if (tipo === "kpis") {
                const tienePuntos = kpiIds.some(id => document.getElementById(id)?.textContent === "...");
                if (tienePuntos && dataRecibida) {
                    errorDetectado = true;
                    motivo = "KPIs se quedaron en estado de carga";
                }
            } else if (tipo === "masa") {
                const tieneData = dataRecibida && dataRecibida.length > 0;
                const chartDibujado = chartMasa && chartMasa.data.datasets[0].data.length > 0;
                if (tieneData && !chartDibujado) {
                    errorDetectado = true;
                    motivo = "Gráfico de Masa no se renderizó habiendo datos";
                }
            } else if (tipo === "rendimiento") {
                const tieneData = dataRecibida && dataRecibida.length > 0;
                const chartDibujado = chartRendimiento && chartRendimiento.data.datasets[0].data.length > 0;
                if (tieneData && !chartDibujado) {
                    errorDetectado = true;
                    motivo = "Gráfico de Rendimiento no se renderizó habiendo datos";
                }
            }

            if (errorDetectado) {
                console.error(`[Fallo Visual] ${motivo}. Forzando reparación de interfaz...`);
                reloadInProgress = true;
                window.location.reload();
            } else {
                console.log(`[Integridad] Check ${tipo} OK`);
            }
        }, 1500); // 1.5s para asegurar que Chart.js terminó
    };

    // 2. CAPTURA FRESCA
    const userRole = (localStorage.getItem("userRole") || "").toLowerCase().trim();
    const codigoEscuela = localStorage.getItem("codigoEscuela");
    const token = localStorage.getItem("token");
    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

    const restaurarOpacidad = (selector) => {
        const els = selector ? document.querySelectorAll(selector) : allCards;
        els.forEach(c => c.style.opacity = '1');
    };

    const manejarErrorConexion = (err, containerId) => {
        if (err.name === 'AbortError') return;
        console.error(`[Error de Conexión]`, err);
        restaurarOpacidad();
        
        const container = document.getElementById(containerId)?.closest('.card-chart') || document.querySelector('.card-container');
        if (container) {
            const existingMsg = container.querySelector('.no-data-msg');
            if (existingMsg) existingMsg.remove();
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'no-data-msg';
            errorDiv.style = "text-align: center; color: #d9534f; padding: 20px; background: #f9f2f4; border-radius: 8px; margin: 10px;";
            errorDiv.innerHTML = `
                <p><b>⚠️ Error de Conexión</b></p>
                <p style="font-size: 12px;">No se pudo establecer contacto con el servidor (Render).</p>
                <p style="font-size: 11px; margin-top: 5px;">Asegúrese de que la API esté encendida o espere unos segundos a que se reactive.</p>
            `;
            container.appendChild(errorDiv);
        }
    };

    // 3. PARÁMETROS
    const filteredParams = new URLSearchParams();
    if (carreraSeleccionada) filteredParams.append("codigo_carrera", carreraSeleccionada);
    if (userRole === "director" && codigoEscuela) filteredParams.append("codigo_escuela", codigoEscuela);

    const masaParams = new URLSearchParams(filteredParams);
    if (periodo) masaParams.append("periodo", periodo);

    // 4. PETICIONES
    
    // KPIs
    fetch(`${BASE_API_DASH}/dashboard/resumen/${periodo}?${filteredParams.toString()}`, { headers, signal })
        .then(res => {
            if (!res.ok) throw new Error("Respuesta de red no válida");
            return res.json();
        })
        .then(data => {
            if (signal.aborted) return;
            document.getElementById("promedio").textContent = Number(data.promedio_general || 0).toFixed(2);
            document.getElementById("tasaAprobacion").textContent = `${Number(data.indice_aprobacion || 0).toFixed(1)}%`;
            document.getElementById("totalEstudiantes").textContent = data.total_estudiantes || 0;
            document.getElementById("materiasCriticas").textContent = data.secciones_criticas || 0;
            document.querySelectorAll('.card').forEach(c => c.style.opacity = '1');
            validarIntegridadVisual("kpis", data);
        })
        .catch(err => manejarErrorConexion(err, "promedio"));

    // Masa
    fetch(`${BASE_API_DASH}/dashboard/masa-estudiantil?${masaParams.toString()}`, { headers, signal })
        .then(res => {
            if (!res.ok) throw new Error("Respuesta de red no válida");
            return res.json();
        })
        .then(data => {
            if (signal.aborted) return;
            const cardMasa = document.getElementById('chartMasa')?.closest('.card-chart');
            if (cardMasa) cardMasa.style.opacity = '1';
            
            if (data && data.length > 0) {
                dibujarChartMasa(data.map(i => i.nombre_carrera || i.codigo_carrera), data.map(i => i.total_general));
            } else {
                if (chartMasa) { chartMasa.destroy(); chartMasa = null; }
            }
            validarIntegridadVisual("masa", data);
        })
        .catch(err => manejarErrorConexion(err, "chartMasa"));

    // Rendimiento
    fetch(`${BASE_API_DASH}/dashboard/rendimiento/${periodo}?${filteredParams.toString()}`, { headers, signal })
        .then(res => {
            if (!res.ok) throw new Error("Respuesta de red no válida");
            return res.json();
        })
        .then(data => {
            if (signal.aborted) return;
            const cardRend = document.getElementById('chartRendimiento')?.closest('.card-chart');
            if (cardRend) cardRend.style.opacity = '1';
            
            if (data && data.length > 0) {
                document.getElementById('chartRendimiento').style.display = 'block';
                const top5 = data.sort((a, b) => a.promedio - b.promedio).slice(0, 5).sort((a, b) => b.promedio - a.promedio);
                dibujarChartRendimiento(top5.map(i => i.nombre_materia || i.codigo_materia), top5.map(i => i.promedio));
            } else {
                if (chartRendimiento) { chartRendimiento.destroy(); chartRendimiento = null; }
                document.getElementById('chartRendimiento').style.display = 'none';
                if (cardRend && !cardRend.querySelector('.no-data-msg')) {
                    const msgDiv = document.createElement('div');
                    msgDiv.className = 'no-data-msg';
                    msgDiv.style = "text-align: center; color: #666; padding: 20px;";
                    msgDiv.innerHTML = `<p>No hay datos en el periodo ${periodo}.</p>`;
                    cardRend.appendChild(msgDiv);
                }
            }
            validarIntegridadVisual("rendimiento", data);
        })
        .catch(err => manejarErrorConexion(err, "chartRendimiento"));
}

// Cargar periodos desde la base de datos
async function cargarPeriodosFiltro() {
    const selPeriodo = document.getElementById("filtroPeriodoGlobal");
    if (!selPeriodo) return;

    try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${BASE_API_DASH}/dashboard/periodos`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const periodosDisponibles = await res.json();

        if (!periodosDisponibles || periodosDisponibles.length === 0) {
            selPeriodo.innerHTML = "<option value=''>Sin datos</option>";
            return;
        }

        selPeriodo.innerHTML = "";
        periodosDisponibles.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p; 
            const [cuatri, anio] = p.split("-");
            opt.textContent = `Periodo ${parseInt(cuatri)} - ${anio}`;
            selPeriodo.appendChild(opt);
        });

        // Restaurar filtro guardado o seleccionar el primero
        const saved = sessionStorage.getItem("lastPeriodo");
        if (saved && [...selPeriodo.options].some(o => o.value === saved)) {
            selPeriodo.value = saved;
        } else {
            selPeriodo.selectedIndex = 0;
        }

    } catch (err) {
        console.error("Error cargando periodos:", err);
        selPeriodo.innerHTML = "<option value=''>Error al cargar</option>";
    }
}

// Cargar carreras disponibles en el selector
async function cargarCarrerasFiltro() {
    const selector = document.getElementById("filtroCarreraRendimiento");
    if (!selector) return;

    const userRole = (localStorage.getItem("userRole") || "").toLowerCase().trim();
    const codigoEscuela = localStorage.getItem("codigoEscuela");
    const token = localStorage.getItem("token");

    let url = `${BASE_API_DASH}/carreras/`;
    if (userRole === "director" && codigoEscuela) {
        url += `?codigo_escuela=${codigoEscuela}`;
    }

    try {
        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const carreras = await res.json();
        
        selector.innerHTML = '<option value="">Todas las Carreras</option>';
        
        carreras.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.codigo;
            opt.textContent = c.nombre;
            selector.appendChild(opt);
        });

        // Restaurar filtro guardado
        const saved = sessionStorage.getItem("lastCarrera");
        if (saved && [...selector.options].some(o => o.value === saved)) {
            selector.value = saved;
        }
    } catch (err) {
        console.error("Error cargando carreras para filtro:", err);
    }
}

// Restricciones de interfaz para el Director
function aplicarRestriccionesDirector() {
    const userRole = (localStorage.getItem("userRole") || "").toLowerCase().trim();
    if (userRole === "director") {
        const sidebar = document.getElementById("sidebar");
        if (sidebar) {
            const btns = sidebar.querySelectorAll(".dropdown-btn");
            btns.forEach(btn => {
                if (btn.innerText.includes("Gestión Académica") || btn.innerText.includes("Datos")) {
                    btn.style.display = "none";
                    if (btn.nextElementSibling) btn.nextElementSibling.style.display = "none";
                }
            });
        }
    }
}

// FUNCIONES PARA DIBUJAR LOS GRÁFICOS
function dibujarChartMasa(labels, data) {
    const ctx = document.getElementById('chartMasa');
    if (!ctx) return;
    
    if (chartMasa) chartMasa.destroy();
    
    chartMasa = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#006837', '#0B3C5D', '#ffc107', '#17a2b8', '#6c757d']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: { boxWidth: 12, font: { size: 11 } }
                },
                datalabels: {
                    color: '#fff',
                    formatter: (value, ctx) => {
                        let sum = 0;
                        let dataArr = ctx.chart.data.datasets[0].data;
                        dataArr.map(d => sum += d);
                        return (value * 100 / sum).toFixed(1) + "%";
                    },
                    font: { weight: 'bold', size: 12 }
                }
            }
        }
    });
}

function dibujarChartRendimiento(labels, data) {
    const ctx = document.getElementById('chartRendimiento');
    if (!ctx) return;

    if (chartRendimiento) chartRendimiento.destroy();

    chartRendimiento = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Promedio',
                data: data,
                backgroundColor: '#006837',
                borderRadius: 5,
                maxBarThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                datalabels: {
                    display: true,
                    anchor: 'end',
                    align: 'top',
                    color: '#006837',
                    font: { weight: 'bold' },
                    formatter: (value) => Number(value).toFixed(1)
                }
            },
            scales: { 
                y: { beginAtZero: true, max: 100, grid: { display: false } },
                x: { grid: { display: false }, ticks: { font: { size: 10 } } }
            }
        }
    });
}

// Inicialización Única
document.addEventListener("DOMContentLoaded", async () => {
    await cargarPeriodosFiltro();
    await cargarCarrerasFiltro();
    aplicarRestriccionesDirector();
    actualizarDashboard();
});
