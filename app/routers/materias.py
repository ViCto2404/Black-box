from fastapi import APIRouter, HTTPException, Query
from app.services import materias as svc
from app.models.materia import MateriaCreate, MateriaUpdate

router = APIRouter(prefix="/materias", tags=["Materias"])

@router.get("/")
def listar_materias(
    estado:         str = Query(default=None),
    codigo_carrera: str = Query(default=None)
):
    return svc.get_todas_materias(estado, codigo_carrera)

@router.get("/{codigo}")
def obtener_materia(codigo: str):
    materia = svc.get_materia_por_codigo(codigo)
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return materia

@router.post("/", status_code=201)
def crear_materia(payload: MateriaCreate):
    materia, error = svc.crear_materia(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return materia

@router.put("/{codigo}")
def actualizar_materia(codigo: str, payload: MateriaUpdate):
    materia, error = svc.actualizar_materia(codigo, payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return materia

@router.delete("/{codigo}", status_code=204)
def eliminar_materia(codigo: str):
    ok, error = svc.eliminar_materia(codigo)
    if error:
        raise HTTPException(status_code=404, detail=error)