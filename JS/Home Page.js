// Registrar el plugin de datalabels
Chart.register(ChartDataLabels);

let chartMasa, chartRendimiento;

async function actualizarDashboard() {
    const periodo = document.getElementById("filtroPeriodo").value;
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
    let urlResumen = `${API_URL}/dashboard/resumen/${periodo}${params}`;
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

    // 2. Gráfico de Masa Estudiantil (Solo se carga si NO hay una carrera específica seleccionada o al inicio)
    // El gráfico de masa es por carrera, si filtramos por una, el pastel no tiene sentido.
    // Pero para evitar que desaparezca, lo cargamos siempre con el filtro de escuela.
    const urlMasa = `${API_URL}/dashboard/masa-estudiantil${params}`;
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
    fetch(`${API_URL}/dashboard/rendimiento/${periodo}${params_rendimiento}`)
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

// Cargar carreras disponibles en el selector
async function cargarCarrerasFiltro() {
    const selector = document.getElementById("filtroCarreraRendimiento");
    if (!selector) return;

    const userRole = (localStorage.getItem("userRole") || "").toLowerCase().trim();
    const codigoEscuela = localStorage.getItem("codigoEscuela");

    let url = `${API_URL}/carreras/`;
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
document.addEventListener("DOMContentLoaded", () => {
    cargarCarrerasFiltro();
    aplicarRestriccionesDirector();
    actualizarDashboard();
});
