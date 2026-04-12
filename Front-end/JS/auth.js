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
            // Guardamos los datos según tu LoginResponse
            // access_token es vital para futuras peticiones protegidas
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("userRole", data.rol);
            localStorage.setItem("userName", data.nombre);
            localStorage.setItem("id_unphu", data.id_unphu);

            alert(`Bienvenido, ${data.nombre}`);

            // REDIRECCIÓN SEGÚN ROL
            if (data.rol.toLowerCase() === "estudiante") {
                window.location.href = "Formularios.html";
            } else {
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
        fetch(`${API}/auth/register`, { 
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

/**
 * cerrarSesion - Sincronizado con el Header del Backend
 */
function cerrarSesion() {
    const token = localStorage.getItem("token");

    // REGLA: Enviamos la petición al servidor para invalidar el token
    fetch(`${API}/auth/logout`, {
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