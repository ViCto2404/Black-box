from fastapi import APIRouter, HTTPException, Query
from app.services import escuelas as svc
from app.models.escuela import EscuelaCreate, EscuelaUpdate

router = APIRouter(prefix="/escuelas", tags=["Escuelas"])

@router.get("/")
def listar_escuelas(estado: str = Query(default=None)):
    return svc.get_todas_escuelas(estado)

@router.get("/{codigo}")
def obtener_escuela(codigo: str):
    escuela = svc.get_escuela_por_codigo(codigo)
    if not escuela:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")
    return escuela

@router.post("/", status_code=201)
def crear_escuela(payload: EscuelaCreate):
    escuela, error = svc.crear_escuela(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return escuela

@router.put("/{codigo}")
def actualizar_escuela(codigo: str, payload: EscuelaUpdate):
    escuela, error = svc.actualizar_escuela(codigo, payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return escuela

@router.delete("/{codigo}", status_code=204)
def eliminar_escuela(codigo: str):
    ok, error = svc.eliminar_escuela(codigo)
    if error:
        raise HTTPException(status_code=404, detail=error)