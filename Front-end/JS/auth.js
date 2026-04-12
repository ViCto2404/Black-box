/**
 * auth.js - Sincronizado con el Router de Autenticación [/auth]
 */
/**
 * LÓGICA DE REDIRECCIÓN CENTRALIZADA
 * Se usa tanto al hacer login como al verificar una sesión existente.
 */
function redireccionarSegunRol(rol, estado, escuela) {
    rol = (rol || "").toLowerCase().trim();
    estado = (estado || "activo").toLowerCase().trim();

    if (estado === "inactivo") {
        window.location.href = "acceso_restringido.html";
    } 
    else if (rol === "estudiante") {
        window.location.href = "formulario_feedback.html";
    } 
    else if (rol === "profesor") {
        window.location.href = "acceso_restringido.html";
    }
    else if (rol === "director") {
        if (!escuela || escuela === "null" || escuela === "undefined") {
            window.location.href = "acceso_restringido.html";
        } else {
            window.location.href = "Home.html";
        }
    }
    else {
        window.location.href = "Home.html";
    }
}

/**
 * VERIFICAR SESIÓN ACTIVA
 * Si el usuario ya está logueado y trata de entrar al login, lo mandamos a su sitio.
 */
function verificarSesionActiva() {
    const token = localStorage.getItem("token");
    const currentPath = window.location.pathname;

    if (token && (currentPath.endsWith("login.html") || currentPath === "/" || currentPath.endsWith("/"))) {
        const rol = localStorage.getItem("userRole");
        const estado = localStorage.getItem("userStatus");
        const escuela = localStorage.getItem("codigoEscuela");
        
        console.log("Sesión detectada, redirigiendo...");
        redireccionarSegunRol(rol, estado, escuela);
    }
}

// Ejecutar verificación de inmediato
verificarSesionActiva();

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", function(e) {
        e.preventDefault();
        
        const payload = {
            email: document.getElementById("email").value, 
            password: document.getElementById("password").value
        };

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
            
            localStorage.clear();

            localStorage.setItem("token", data.access_token);
            localStorage.setItem("userRole", data.rol);
            localStorage.setItem("userName", data.nombre);
            localStorage.setItem("id_unphu", data.id_unphu);
            
            if (data.codigo_escuela) {
                localStorage.setItem("codigoEscuela", data.codigo_escuela);
            }

            if (data.codigo_carrera) {
                localStorage.setItem("codigoCarrera", data.codigo_carrera);
            }

            if (data.estado) {
                localStorage.setItem("userStatus", data.estado);
            }

            alert(`Bienvenido, ${data.nombre}`);

            // Aplicar la redirección usando la nueva función
            redireccionarSegunRol(data.rol, data.estado, data.codigo_escuela);
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
            id_unphu: document.getElementById("id_unphu").value,
            nombre: document.getElementById("nombre").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        };

        console.log("Enviando registro de administrador:", payload);

        fetch(`${API_URL}/auth/crear-administrador`, { 
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || "Error al registrar administrador");
            }
            alert("Administrador creado con éxito. ¡Ya puede iniciar sesión!");
            window.location.href = "login.html";
        })
        .catch(err => alert("Error de registro: " + err.message));
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