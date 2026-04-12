/**
 * auth.js - Sincronizado con el Router de Autenticación [/auth]
 */
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", function(e) {
        e.preventDefault();
        
        // REGLA: Aunque el ID en tu HTML sea "usuario", 
        // tu API espera el campo "email"
        const payload = {
            email: document.getElementById("email").value, 
            password: document.getElementById("password").value
        };

        // REGLA: El router tiene el prefijo "/auth"
        fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Credenciales incorrectas");
            }
            return res.json();
        })
        .then(data => {
            console.log("DEBUG: Respuesta JSON del servidor:", JSON.stringify(data, null, 2));
            
            // Limpiar datos previos para evitar basura de sesiones anteriores
            localStorage.clear();

            // Guardamos los datos según tu LoginResponse
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("userRole", data.rol);
            localStorage.setItem("userName", data.nombre);
            localStorage.setItem("id_unphu", data.id_unphu);
            
            console.log("DEBUG: Valor de codigo_escuela recibido:", data.codigo_escuela);
            
            if (data.codigo_escuela) {
                localStorage.setItem("codigoEscuela", data.codigo_escuela);
                console.log("DEBUG: codigoEscuela guardado exitosamente en localStorage:", localStorage.getItem("codigoEscuela"));
            }

            if (data.codigo_carrera) {
                localStorage.setItem("codigoCarrera", data.codigo_carrera);
                console.log("DEBUG: codigoCarrera guardado exitosamente en localStorage:", localStorage.getItem("codigoCarrera"));
            }

            if (data.estado) {
                localStorage.setItem("userStatus", data.estado);
            }

            const rol = data.rol.toLowerCase().trim();
            const estado = (data.estado || "activo").toLowerCase().trim();
            const escuela = data.codigo_escuela;

            console.log("DEBUG REDIRECT: Rol:", rol);
            console.log("DEBUG REDIRECT: Estado:", estado);
            console.log("DEBUG REDIRECT: Escuela:", escuela);

            alert(`Bienvenido, ${data.nombre}`);

            // LÓGICA DE REDIRECCIÓN CENTRALIZADA
            if (estado === "inactivo") {
                console.log("REDIRECCIONANDO A: acceso_restringido.html (USUARIO INACTIVO)");
                window.location.href = "acceso_restringido.html";
            } 
            else if (rol === "estudiante") {
                window.location.href = "formulario_feedback.html";
            } 
            else if (rol === "profesor") {
                window.location.href = "acceso_restringido.html";
            }
            else if (rol === "director") {
                if (!escuela || escuela === "null") {
                    window.location.href = "acceso_restringido.html";
                } else {
                    window.location.href = "Home.html";
                }
            }
            else {
                window.location.href = "Home.html";
            }
        })
        .catch(err => {
            alert("Error de acceso: " + err.message);
        });
    });
}

// --- Lógica de Registro (Añadir a auth.js) ---
const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", function(e) {
        e.preventDefault();
        
        const payload = {
            nombre: document.getElementById("nombre").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value,
            rol: document.getElementById("rol").value
        };

        // Nota: Verifica si tu router de registro también usa el prefijo /auth
        // Si no lo usa, quita el '/auth' de la URL
        fetch(`${API_URL}/auth/register`, { 
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Error al registrar usuario");
            }
            alert("Registro exitoso. ¡Ya puedes iniciar sesión!");
            window.location.href = "login.html";
        })
        .catch(err => alert(err.message));
    });
}

// --- Lógica de Cambio de Contraseña ---
const changePasswordForm = document.getElementById("changePasswordForm");

if (changePasswordForm) {
    changePasswordForm.addEventListener("submit", function(e) {
        e.preventDefault();

        const payload = {
            email: document.getElementById("email").value,
            password_actual: document.getElementById("password_actual").value,
            password_nuevo: document.getElementById("password_nuevo").value,
            password_nuevo_confirmacion: document.getElementById("password_confirmacion").value
        };

        if (payload.password_nuevo !== payload.password_nuevo_confirmacion) {
            alert("Las nuevas contraseñas no coinciden.");
            return;
        }

        fetch(`${API_URL}/auth/cambiar-password`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || "Error al actualizar la contraseña");
            }
            alert("Contraseña actualizada correctamente. ¡Ya puedes iniciar sesión con tu nueva contraseña!");
            window.location.href = "login.html";
        })
        .catch(err => {
            alert("Error: " + err.message);
        });
    });
}

/**
 * cerrarSesion - Sincronizado con el Header del Backend
 */
function cerrarSesion() {
    const token = localStorage.getItem("token");

    // REGLA: Enviamos la petición al servidor para invalidar el token
    fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        headers: { 
            // Tal cual lo pide tu FastAPI: Header(...)
            "Authorization": `Bearer ${token}` 
        }
    })
    .then(res => {
        if (res.ok || res.status === 401) {
            // Limpiamos el localStorage pase lo que pase en el servidor
            localStorage.clear();
            alert("Sesión cerrada correctamente.");
            window.location.href = "login.html";
        }
    })
    .catch(err => {
        console.error("Error al cerrar sesión:", err);
        // Fallback: Si el servidor falla, cerramos localmente de todos modos
        localStorage.clear();
        window.location.href = "login.html";
    });
}