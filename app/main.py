from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://black-box-bryr.onrender.com",
    ],
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

@app.get("/")
def root():
    return {"message": "UNPHU Academic Insights API Corriendo"}