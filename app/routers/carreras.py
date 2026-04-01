from fastapi import APIRouter, HTTPException, Query
from app.services import carreras as svc
from app.models.carrera import CarreraCreate, CarreraUpdate

router = APIRouter(prefix="/carreras", tags=["Carreras"])


@router.get("/")
def listar_carreras(
    estado:         str = Query(default=None),
    codigo_escuela: str = Query(default=None)
):
    return svc.get_todas_carreras(estado, codigo_escuela)


@router.get("/{codigo}")
def obtener_carrera(codigo: str):
    carrera = svc.get_carrera_por_codigo(codigo)
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    return carrera


@router.post("/", status_code=201)
def crear_carrera(payload: CarreraCreate):
    carrera, error = svc.crear_carrera(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return carrera


@router.put("/{codigo}")
def actualizar_carrera(codigo: str, payload: CarreraUpdate):
    carrera, error = svc.actualizar_carrera(codigo, payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return carrera


@router.delete("/{codigo}", status_code=204)
def eliminar_carrera(codigo: str):
    ok, error = svc.eliminar_carrera(codigo)
    if error:
        raise HTTPException(status_code=400, detail=error)