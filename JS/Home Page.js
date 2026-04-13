// Registrar el plugin de datalabels
Chart.register(ChartDataLabels);

let chartMasa, chartRendimiento;

// Determinar la URL de la API de forma dinámica
let BASE_API = (typeof API_URL !== 'undefined') ? API_URL : "https://black-box-bryr.onrender.com";

// Si estamos en localhost, usar preferiblemente el backend local
if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    BASE_API = "http://127.0.0.1:8000";
}

async function actualizarDashboard() {
    const anio = document.getElementById("filtroAnio")?.value;
    const cuatri = document.getElementById("filtroPeriodoCuatri")?.value;
    
    // Si los selectores no están listos o no tienen valor, no continuar
    if (!anio || !cuatri) return;

    const periodo = `${cuatri}-${anio}`;
    const carreraSeleccionada = document.getElementById("filtroCarreraRendimiento").value;

    // Obtener datos de sesión
    const rawRole = localStorage.getItem("userRole") || "";
    const userRole = rawRole.toLowerCase().trim();
    const codigoEscuela = localStorage.getItem("codigoEscuela");

    let params = "";
    let params_rendimiento = "";

    // Si es director, aplicar filtro de escuela
    if (userRole === "director") {
        if (codigoEscuela && codigoEscuela !== "null" && codigoEscuela !== "undefined") {
            params = `?escuela=${codigoEscuela}`;
            params_rendimiento = `?codigo_escuela=${codigoEscuela}`;
        }
    }

    // El filtro de carrera solo afecta a Rendimiento y Resumen (si el API lo soporta)
    if (carreraSeleccionada) {
        params_rendimiento += (params_rendimiento ? "&" : "?") + `codigo_carrera=${carreraSeleccionada}`;
    }

    // 1. Cargar Resumen (KPIs)
    let urlResumen = `${BASE_API}/dashboard/resumen/${periodo}${params}`;
    if (carreraSeleccionada) {
        urlResumen += (urlResumen.includes("?") ? "&" : "?") + `codigo_carrera=${carreraSeleccionada}`;
    }

    fetch(urlResumen)
        .then(res => res.json())
        .then(data => {
            document.getElementById("promedio").textContent = Number(data.promedio_general || 0).toFixed(2);
            document.getElementById("tasaAprobacion").textContent = `${Number(data.indice_aprobacion || 0).toFixed(1)}%`;
            document.getElementById("totalEstudiantes").textContent = data.total_estudiantes || 0;
            document.getElementById("materiasCriticas").textContent = data.secciones_criticas || 0;
        })
        .catch(err => console.error("Error en resumen:", err));

    // 2. Gráfico de Masa Estudiantil (Filtrado por escuela y periodo)
    const urlMasa = `${BASE_API}/dashboard/masa-estudiantil${params}${params ? '&' : '?'}periodo=${periodo}`;
    fetch(urlMasa)
        .then(res => res.json())
        .then(data => {
            if (data && data.length > 0) {
                const labels = data.map(i => i.nombre_carrera || i.codigo_carrera);
                const valores = data.map(i => i.total_general);
                dibujarChartMasa(labels, valores);
            }
        })
        .catch(err => console.error("Error en masa estudiantil:", err));

    // 3. Gráfico de Rendimiento (TOP 5 PEOR RENDIMIENTO)
    fetch(`${BASE_API}/dashboard/rendimiento/${periodo}${params_rendimiento}`)
        .then(res => res.json())
        .then(data => {
            if (data && data.length > 0) {
                const top5Peores = data
                    .sort((a, b) => a.promedio - b.promedio)
                    .slice(0, 5)
                    .sort((a, b) => b.promedio - a.promedio);

                const labels = top5Peores.map(i => i.nombre_materia || i.codigo_materia);
                const valores = top5Peores.map(i => i.promedio);
                dibujarChartRendimiento(labels, valores);
            } else {
                // Si no hay datos, limpiar gráfico para no mostrar basura
                if (chartRendimiento) chartRendimiento.destroy();
            }
        })
        .catch(err => console.error("Error en rendimiento:", err));
}

// Cargar periodos desde la base de datos
async function cargarPeriodosFiltro() {
    const selAnio = document.getElementById("filtroAnio");
    const selCuatri = document.getElementById("filtroPeriodoCuatri");
    if (!selAnio || !selCuatri) return;

    // Mostrar estado de carga visual
    selAnio.innerHTML = "<option>...</option>";
    selCuatri.innerHTML = "<option>Cargando datos...</option>";

    try {
        console.log("Pidiendo periodos reales a:", `${BASE_API}/dashboard/periodos`);
        const res = await fetch(`${BASE_API}/dashboard/periodos`);
        
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const periodosDisponibles = await res.json();
        console.log("Periodos recibidos de la BD:", periodosDisponibles);

        if (!periodosDisponibles || periodosDisponibles.length === 0) {
            selAnio.innerHTML = "<option value=''>N/A</option>";
            selCuatri.innerHTML = "<option value=''>Sin datos</option>";
            return;
        }

        // Limpiar para llenar con datos reales
        selAnio.innerHTML = "";
        selCuatri.innerHTML = "";

        const anios = [...new Set(periodosDisponibles.map(p => p.split("-")[1]))].sort((a, b) => b - a);
        const cuatris = [...new Set(periodosDisponibles.map(p => p.split("-")[0]))].sort((a, b) => b - a);

        anios.forEach(a => {
            const opt = document.createElement("option");
            opt.value = a; opt.textContent = a;
            selAnio.appendChild(opt);
        });

        cuatris.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c; opt.textContent = `Periodo ${parseInt(c)}`;
            selCuatri.appendChild(opt);
        });

        const masReciente = periodosDisponibles[0].split("-");
        selAnio.value = masReciente[1];
        selCuatri.value = masReciente[0];

    } catch (err) {
        console.error("Error cargando periodos:", err);
        selAnio.innerHTML = "<option value=''>Error</option>";
        selCuatri.innerHTML = "<option value=''>Ver Consola (F12)</option>";
    }
}

// Cargar carreras disponibles en el selector
async function cargarCarrerasFiltro() {
    const selector = document.getElementById("filtroCarreraRendimiento");
    if (!selector) return;

    const userRole = (localStorage.getItem("userRole") || "").toLowerCase().trim();
    const codigoEscuela = localStorage.getItem("codigoEscuela");

    let url = `${BASE_API}/carreras/`;
    if (userRole === "director" && codigoEscuela) {
        url += `?codigo_escuela=${codigoEscuela}`;
    }

    try {
        const res = await fetch(url);
        const carreras = await res.json();
        
        // Limpiar opciones previas (excepto la primera)
        selector.innerHTML = '<option value="">Todas las Carreras</option>';
        
        carreras.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.codigo;
            opt.textContent = c.nombre;
            selector.appendChild(opt);
        });
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
