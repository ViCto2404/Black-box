/**
 * feedback.js - Gestión del Buzón de Feedback Estudiantil
 */

document.addEventListener("DOMContentLoaded", function() {
    const feedbackForm = document.getElementById("feedbackForm");

    if (feedbackForm) {
        feedbackForm.addEventListener("submit", function(e) {
            e.preventDefault();

            // 1. Obtener valores del formulario
            const tipo = document.getElementById("tipo").value;
            
            // Obtener múltiples categorías seleccionadas
            const selectCategoria = document.getElementById("categoria");
            const categoriasSeleccionadas = Array.from(selectCategoria.selectedOptions).map(opt => opt.value).join(", ");
            
            const descripcion = document.getElementById("descripcion").value;
            const esAnonimo = document.getElementById("anonimo").checked;

            // 2. Preparar el payload según FeedbackCreate
            // El backend espera: id_estudiante, aspectos_evaluar, comentario, es_anonimo
            const payload = {
                id_estudiante: esAnonimo ? null : localStorage.getItem("id_unphu"),
                aspectos_evaluar: `${tipo.toUpperCase()}: ${categoriasSeleccionadas}`,
                comentario: descripcion,
                es_anonimo: esAnonimo
            };

            console.log("Enviando feedback:", payload);

            // 3. Enviar a la API
            fetch(`${API_URL}/feedback/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(payload)
            })
            .then(async res => {
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Error al enviar el feedback");
                }
                return res.json();
            })
            .then(data => {
                alert("¡Gracias! Tu feedback ha sido enviado correctamente.");
                feedbackForm.reset();
                // Actualizar contador de caracteres
                const contador = document.getElementById("contador");
                if (contador) contador.textContent = "0 / 300 caracteres";
            })
            .catch(err => {
                alert("No se pudo enviar el feedback: " + err.message);
            });
        });
    }
});
