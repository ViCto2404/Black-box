from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Annotated
from app.services import calificaciones as svc
from app.services.validacion import procesar_archivo
from app.models.calificacion import CalificacionCreate

router = APIRouter(prefix="/calificaciones", tags=["calificaciones"])

@router.get("/")
def listar_calificaciones(
    periodo:        str = Query(default=None),
    id_estudiante:  str = Query(default=None),
    codigo_materia: str = Query(default=None),
    id_seccion:     int = Query(default=None)
):
    return svc.get_calificaciones(periodo, id_estudiante, codigo_materia, id_seccion)

@router.post("/", status_code=201)
def crear_calificacion(payload: CalificacionCreate):
    calificacion, error = svc.crear_calificacion(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return calificacion

@router.patch("/{id}/nota")
def actualizar_nota(id: int, nota: float = Query(...)):
    calificacion, error = svc.actualizar_calificacion(id, nota)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return calificacion

@router.delete("/{id}", status_code=204)
def eliminar_calificacion(id:int):
    ok, error = svc.eliminar_calificacion(id)
    if error:
        raise HTTPException(status_code=404, detail=error)

@router.post("/carga-masiva")
async def carga_masiva(archivo: Annotated[UploadFile, File()]):
    if not archivo.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Formato no soportado. Use CSV o Excel (.csv, .xlsx, .xls)"
        )

    contenido = await archivo.read()

    if len(contenido) == 0:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío"
        )

    registros, errores_validacion = procesar_archivo(contenido, archivo.filename)

    if errores_validacion:
        raise HTTPException(
            status_code=422,
            detail={
                "mensaje": "El archivo contiene errores de validación",
                "errores": errores_validacion
            }
        )

    resultado = svc.carga_masiva(registros)
    return {
        "mensaje":    f"{resultado['insertados']} calificaciones insertadas correctamente",
        "insertados": resultado["insertados"],
        "errores":    resultado["errores"]
    }