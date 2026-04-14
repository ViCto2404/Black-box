from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.routers import (
    dashboard, estudiantes, calificaciones, 
    feedback, reportes, escuelas, profesores,
    materias, secciones, directores, carreras, 
    auth)

app = FastAPI(
    title="UNPHU Academic Insights API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(escuelas.router)
app.include_router(profesores.router)
app.include_router(materias.router)
app.include_router(secciones.router)
app.include_router(estudiantes.router)
app.include_router(calificaciones.router)
app.include_router(feedback.router)
app.include_router(reportes.router)
app.include_router(directores.router)
app.include_router(carreras.router)
app.include_router(auth.router)

# --- Servir archivos estáticos del Front-end ---
if os.path.exists("JS"):
    app.mount("/JS", StaticFiles(directory="JS"), name="js")
if os.path.exists("CSS"):
    app.mount("/CSS", StaticFiles(directory="CSS"), name="css")

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "UNPHU Academic Insights API Corriendo"}

@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        return FileResponse(file_path)
    return {"error": "Archivo no encontrado"}