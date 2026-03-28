from fastapi import APIRouter, HTTPException, Query
from app.services import profesores as svc
from app.models.profesor import ProfesorCreate, ProfesorUpdate

router = APIRouter(prefix="/profesores", tags=["Profesores"])

@router.get("/")
def listar_profesores(
    estado:         str = Query(default=None),
    codigo_carrera: str = Query(default=None)
):
    return svc.get_todos_profesores(estado, codigo_carrera)

@router.get("/{id_profesor}")
def obtener_profesor(id_profesor: str):
    profesor = svc.get_profesor_por_id(id_profesor)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@router.post("/", status_code=201)
def crear_profesor(payload: ProfesorCreate):
    profesor, error = svc.crear_profesor(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return profesor

@router.put("/{id_profesor}")
def actualizar_profesor(id_profesor: str, payload: ProfesorUpdate):
    profesor, error = svc.actualizar_profesor(id_profesor, payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return profesor

@router.delete("/{id_profesor}", status_code=204)
def eliminar_profesor(id_profesor: str):
    ok, error = svc.eliminar_profesor(id_profesor)
    if error:
        raise HTTPException(status_code=404, detail=error)