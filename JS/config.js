// Configuración global de la API
// Descomenta la línea de LOCALHOST para pruebas locales con tu API corriendo en tu PC
// Por defecto, se usa la API de Render si no estás en localhost
const API_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "https://black-box-bryr.onrender.com" // Cambia a "http://127.0.0.1:8000" para pruebas locales
    : "https://black-box-bryr.onrender.com";

console.log("API configurada en:", API_URL);
console.log("Host actual:", window.location.hostname);
