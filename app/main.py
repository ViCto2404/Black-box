from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    dashboard, estudiantes, calificaciones, 
    feedback, reportes, escuelas, profesores,
    materias, secciones, directores)

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

@app.get("/")
def root():
    return {"message": "UNPHU Academic Insights API Corriendo"}