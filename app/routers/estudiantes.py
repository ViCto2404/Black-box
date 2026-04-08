from fastapi import APIRouter, HTTPException, Query
from app.services import estudiantes as svc
from app.models.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponde

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

@router.get("/")
def listar_estudiantes(
    carrera: str = Query(default=None),
    estado: str = Query(default=None)
):
    return svc.get_todos_estudiantes(carrera, estado)

@router.get("/{id_unphu}")
def obtener_estudiante(id_unphu: str):
    estudiante = svc.get_estudiante_por_id(id_unphu)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@router.post("/", status_code=201)
def crear_estudiante(payload: EstudianteCreate):
    estudiante, error = svc.crear_estudiante(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return estudiante

@router.patch("/{id_unphu}")
def actualizar_estudiante(id_unphu: str, payload: EstudianteUpdate):
    estudiante, error = svc.actualizar_estudiante(id_unphu, payload.model_dump(exclude_unset=True))
    if error:
        # Si error es un string (como "Estudiante no encontrado"), lanzamos 404 o 400
        raise HTTPException(status_code=400, detail=error)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@router.patch("/{id_unphu}/estado")
def cambiar_estado(id_unphu: str, estado: str = Query(...)):
    estudiante, error = svc.actualizar_estado(id_unphu, estado)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return estudiante

@router.delete("/{id_unphu}")
def eliminar_estudiante(id_unphu: str):
    ok, error = svc.eliminar_estudiante(id_unphu)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {"status": "success", "message": "Estudiante eliminado correctamente"}
