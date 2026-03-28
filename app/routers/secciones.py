from fastapi import APIRouter, HTTPException, Query
from app.services import secciones as svc
from app.models.seccion import SeccionCreate, SeccionUpdate

router = APIRouter(prefix="/secciones", tags=["Secciones"])

@router.get("/")
def listar_secciones(
    periodo: str = Query(default=None),
    materia: str = Query(default=None),
    estado:  str = Query(default=None)
):
    return svc.get_todas_secciones(periodo, materia, estado)

@router.get("/{id}")
def obtener_seccion(id: int):
    seccion = svc.get_seccion_por_id(id)
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    return seccion

@router.post("/", status_code=201)
def crear_seccion(payload: SeccionCreate):
    seccion, error = svc.crear_seccion(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return seccion

@router.put("/{id}")
def actualizar_seccion(id: int, payload: SeccionUpdate):
    seccion, error = svc.actualizar_seccion(id, payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return seccion

@router.delete("/{id}", status_code=204)
def eliminar_seccion(id: int):
    ok, error = svc.eliminar_seccion(id)
    if error:
        raise HTTPException(status_code=404, detail=error)