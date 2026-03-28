from fastapi import APIRouter, HTTPException, Query
from app.services import directores as svc
from app.models.director import DirectorCreate, DirectorUpdate

router = APIRouter(prefix="/directores", tags=["Directores"])


@router.get("/")
def listar_directores(codigo_escuela: str = Query(default=None)):
    return svc.get_todos_directores(codigo_escuela)


@router.get("/{id_unphu}")
def obtener_director(id_unphu: str):
    director = svc.get_director_por_id(id_unphu)
    if not director:
        raise HTTPException(status_code=404, detail="Director no encontrado")
    return director


@router.post("/", status_code=201)
def crear_director(payload: DirectorCreate):
    director, error = svc.crear_director(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return director


@router.put("/{id_unphu}")
def actualizar_director(id_unphu: str, payload: DirectorUpdate):
    director, error = svc.actualizar_director(id_unphu, payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return director


@router.delete("/{id_unphu}", status_code=204)
def eliminar_director(id_unphu: str):
    ok, error = svc.eliminar_director(id_unphu)
    if error:
        raise HTTPException(status_code=400, detail=error)