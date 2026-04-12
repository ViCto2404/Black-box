/**
 * descargarReporte - Conecta con el router /reportes de FastAPI
 */
async function descargarReporte() {
    const periodo = document.getElementById("filtroPeriodo").value;
    const tipoReporte = document.getElementById("tipoReporte").value;
    const formatoSelector = document.getElementById("formatoReporte");
    const formato = formatoSelector.value;

    // Si no hay formato seleccionado (ej. al inicio), no hacemos nada
    if (!formato) return;

    // Bloqueamos el selector visualmente
    formatoSelector.disabled = true;
    const originalText = formatoSelector.options[0].text;
    formatoSelector.options[0].text = "⌛ Generando...";

    try {
        let endpoint = "";
        let nombreArchivo = "";

        // Mapeo dinámico según el tipo y periodo
        if (tipoReporte === "resumen") {
            endpoint = `/reportes/resumen/${periodo}?format=${formato}`;
            nombreArchivo = `Resumen_Academico_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        } else if (tipoReporte === "rendimiento") {
            endpoint = `/reportes/rendimiento/${periodo}?format=${formato}`;
            nombreArchivo = `Rendimiento_Asignaturas_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        } else if (tipoReporte === "criticas") {
            endpoint = `/reportes/criticas/${periodo}?format=${formato}`;
            nombreArchivo = `Materias_Criticas_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        } else if (tipoReporte === "masa") {
            endpoint = `/reportes/masa/${periodo}?format=${formato}`;
            nombreArchivo = `Masa_Estudiantil_${periodo}.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        } else if (tipoReporte === "feedback") {
            endpoint = `/reportes/feedback?format=${formato}`;
            nombreArchivo = `Feedback_Estudiantil.${formato === 'excel' ? 'xlsx' : 'pdf'}`;
        }

        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) throw new Error("Error al generar el archivo");

        const blob = await response.blob();
        const urlDescarga = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = urlDescarga;
        a.download = nombreArchivo;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(urlDescarga);

    } catch (error) {
        console.error("Error:", error);
        alert("No se pudo descargar el reporte: " + error.message);
    } finally {
        // Restauramos el selector
        formatoSelector.disabled = false;
        formatoSelector.options[0].text = originalText;
        formatoSelector.selectedIndex = 0; // Regresa al placeholder
    }
}
