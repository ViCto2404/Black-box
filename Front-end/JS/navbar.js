// --- GESTIÓN DEL SIDEBAR (Toggle) ---
function toggleMenu() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) {
        sidebar.classList.toggle("active");
    }
}

// Cerrar sidebar si hacen click fuera
document.addEventListener("click", function(event) {
    const sidebar = document.getElementById("sidebar");
    const menuBtn = document.querySelector(".menu-btn");

    if (sidebar && sidebar.classList.contains("active")) {
        if (!sidebar.contains(event.target) && !menuBtn.contains(event.target)) {
            sidebar.classList.remove("active");
        }
    }
});

// --- LÓGICA DE PERMISOS POR ROL ---
function aplicarPermisosDeMenu() {
    const rolRaw = localStorage.getItem("userRole") || "";
    const rol = rolRaw.toLowerCase().trim();
    if (!rol) return;

    const sidebarMenu = document.querySelector(".sidebar-menu");
    const menuBtn = document.querySelector(".menu-btn");

    // REGLA: Si es director, ocultar el botón del menú hamburguesa por completo
    if (rol === "director" && menuBtn) {
        menuBtn.style.display = "none";
    }

    if (!sidebarMenu) return;

    const dropdownBtns = sidebarMenu.querySelectorAll(".dropdown-btn");
    const containers = sidebarMenu.querySelectorAll(".dropdown-container");

    if (rol === "estudiante") {
        dropdownBtns.forEach(btn => {
            if (!btn.innerText.includes("Estudiantes")) {
                btn.style.display = "none";
            }
        });
        
        containers.forEach(cont => {
            if (cont.innerHTML.includes("formulario_feedback.html")) {
                cont.style.display = "block"; 
            } else {
                cont.style.display = "none";
            }
        });
    } 
    else if (rol === "admin" || rol === "administrador") {
        const links = sidebarMenu.querySelectorAll("a");
        links.forEach(a => {
            if (a.getAttribute("href") === "formulario_feedback.html") {
                a.style.display = "none";
            }
        });
        
        // Asegurar que el apartado de Usuarios sea visible para Admin
        dropdownBtns.forEach(btn => {
            if (btn.innerText.includes("Usuarios")) {
                btn.style.display = "block";
            }
        });
    }
    else {
        // Para cualquier otro rol (ej. director), ocultamos el apartado de Usuarios si existiera
        dropdownBtns.forEach(btn => {
            if (btn.innerText.includes("Usuarios")) {
                btn.style.display = "none";
                if (btn.nextElementSibling) btn.nextElementSibling.style.display = "none";
            }
        });
    }
}

// --- ACTUALIZAR NOMBRES EN NAVBAR ---
function actualizarInterfazAuth() {
    const nombre = localStorage.getItem("userName");
    const authSection = document.getElementById("nav-auth-section");

    if (nombre && authSection) {
        authSection.innerHTML = `
            <span class="user-welcome" style="color:white; margin-right:15px;">Hola, <b>${nombre}</b></span>
            <a href="#" class="btn-logout" onclick="cerrarSesion()" style="color:white; text-decoration:none; font-weight:bold;">Cerrar Sesión</a>
        `;
    }
}

// --- INICIALIZACIÓN ÚNICA ---
document.addEventListener("DOMContentLoaded", function() {
    aplicarPermisosDeMenu();
    actualizarInterfazAuth();

    // Activar Dropdowns del Sidebar (UNA SOLA VEZ)
    const dropdowns = document.getElementsByClassName("dropdown-btn");
    for (let i = 0; i < dropdowns.length; i++) {
        dropdowns[i].addEventListener("click", function() {
            this.classList.toggle("active");
            const dropdownContent = this.nextElementSibling;
            if (dropdownContent) {
                if (dropdownContent.style.display === "block") {
                    dropdownContent.style.display = "none";
                } else {
                    dropdownContent.style.display = "block";
                }
            }
        });
    }
});
