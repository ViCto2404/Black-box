// Registrar el plugin de datalabels
Chart.register(ChartDataLabels);

let chartMasa, chartRendimiento;
async function actualizarDashboard() {
    const periodo = document.getElementById("filtroPeriodo").value;

    // Obtener datos de sesión
    const rawRole = localStorage.getItem("userRole") || "";
    const userRole = rawRole.toLowerCase().trim();
    const codigoEscuela = localStorage.getItem("codigoEscuela");

    let params = "";
    let params_rendimiento = "";

    console.log("--- DASHBOARD DEBUG ---");
    console.log("Periodo:", periodo);
    console.log("Rol Detectado:", userRole);
    console.log("Escuela en Storage:", codigoEscuela);

    // Si es director, FORZAR el filtro de escuela
    if (userRole === "director") {
        if (codigoEscuela && codigoEscuela !== "null" && codigoEscuela !== "undefined") {
            params = `?escuela=${codigoEscuela}`;
            params_rendimiento = `?codigo_escuela=${codigoEscuela}`;
            console.log("Filtros de Director APLICADOS:", { params, params_rendimiento });
        } else {
            console.error("ALERTA: El usuario es DIRECTOR pero no tiene un CODIGO DE ESCUELA asignado.");
            alert("Atención: No se ha detectado su código de escuela. Los datos podrían ser incompletos.");
        }
    } else {
        console.log("Usuario es Administrador o Estudiante, cargando datos globales.");
    }

    const urlResumen = `${API_URL}/dashboard/resumen/${periodo}${params}`;
    console.log("URL Final Resumen:", urlResumen);
    console.log("-----------------------");

    // 1. Cargar Resumen (KPIs)
    fetch(urlResumen)
        .then(res => res.json())
        .then(data => {
            console.log("Respuesta Recibida:", data);
            
            const promedio = data.promedio_general || 0;
            const tasa = data.indice_aprobacion || 0;
            const total = data.total_secciones_analizadas || 0;
            const criticas = data.secciones_criticas || 0;

            document.getElementById("promedio").textContent = Number(promedio).toFixed(2);
            document.getElementById("tasaAprobacion").textContent = `${Number(tasa).toFixed(1)}%`;
            document.getElementById("totalEstudiantes").textContent = total;
            document.getElementById("materiasCriticas").textContent = criticas;
        })
        .catch(err => console.error("Error en resumen:", err));

    // 2. Gráfico de Masa Estudiantil
    // Para masa estudiantil, si es director, quizas queramos filtrar por las carreras de su escuela
    // Por ahora lo dejamos general o si el API soporta carrera, podriamos filtrar.
    fetch(`${API_URL}/dashboard/masa-estudiantil`)
        .then(res => res.json())
        .then(data => {
            const labels = data.map(i => i.nombre_carrera || i.codigo_carrera);
            const valores = data.map(i => i.total_general);
            dibujarChartMasa(labels, valores);
        })
        .catch(err => console.error("Error en masa estudiantil:", err));

    // 3. Gráfico de Rendimiento
    fetch(`${API_URL}/dashboard/rendimiento/${periodo}${params_rendimiento}`)
        .then(res => res.json())
        .then(data => {
            const labels = data.map(i => i.nombre_materia || i.codigo_materia);
            const valores = data.map(i => i.promedio);
            dibujarChartRendimiento(labels, valores);
        })
        .catch(err => console.error("Error en rendimiento:", err));
}

// Restricciones de interfaz para el Director
function aplicarRestriccionesDirector() {
    const userRole = localStorage.getItem("userRole");
    if (userRole === "director") {
        // Ocultar secciones de gestión en el sidebar
        const sidebar = document.getElementById("sidebar");
        if (sidebar) {
            const gestionBtn = sidebar.querySelector(".dropdown-btn:nth-of-type(1)");
            const datosBtn = sidebar.querySelector(".dropdown-btn:nth-of-type(3)");
            
            if (gestionBtn) {
                gestionBtn.style.display = "none";
                gestionBtn.nextElementSibling.style.display = "none";
            }
            if (datosBtn) {
                datosBtn.style.display = "none";
                datosBtn.nextElementSibling.style.display = "none";
            }
        }
    }
}

// FUNCIONES PARA DIBUJAR LOS GRÁFICOS
function dibujarChartMasa(labels, data) {
    if (chartMasa) chartMasa.destroy();
    const ctx = document.getElementById('chartMasa');
    if (!ctx) return;
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
                    labels: {
                        boxWidth: 12,
                        padding: 20,
                        font: { size: 12 }
                    }
                },
                datalabels: {
                    color: '#fff',
                    formatter: (value, ctx) => {
                        let sum = 0;
                        let dataArr = ctx.chart.data.datasets[0].data;
                        dataArr.map(d => {
                            sum += d;
                        });
                        let percentage = (value * 100 / sum).toFixed(1) + "%";
                        return percentage;
                    },
                    font: {
                        weight: 'bold',
                        size: 14
                    }
                }
            }
        }
    });
}

function dibujarChartRendimiento(labels, data) {
    if (chartRendimiento) chartRendimiento.destroy();
    const ctx = document.getElementById('chartRendimiento');
    if (!ctx) return;
    chartRendimiento = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Promedio de Calificación',
                data: data,
                backgroundColor: '#006837'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 20,
                        font: { size: 12 }
                    }
                },
                datalabels: {
                    display: false // No queremos porcentajes en el gráfico de barras
                }
            },
            scales: { 
                y: { 
                    beginAtZero: true, 
                    max: 100 
                } 
            }
        }
    });
}

// Iniciar al cargar
document.addEventListener("DOMContentLoaded", () => {
    aplicarRestriccionesDirector();
    actualizarDashboard();
});
