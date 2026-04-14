// Configuración global de la API
const API_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://127.0.0.1:8000"
    : "https://black-box-bryr.onrender.com";

console.log("API configurada en:", API_URL);
