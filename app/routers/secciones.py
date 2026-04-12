from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Response
from typing import Annotated
from app.services import secciones as svc
from app.services.validacion import procesar_archivo_secciones
from app.models.seccion import SeccionCreate, SeccionUpdate

router = APIRouter(prefix="/secciones", tags=["Secciones"])

@router.get("/plantilla")
def descargar_plantilla():
    contenido = svc.generar_plantilla_seccion()
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_secciones.xlsx"}
    )

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

    registros, errores_validacion = procesar_archivo_secciones(contenido, archivo.filename)

    if errores_validacion:
        raise HTTPException(
            status_code=422,
            detail={
                "mensaje": "El archivo contiene errores de validación",
                "errores": errores_validacion
            }
        )

    resultado = svc.carga_masiva_secciones(registros)
    return {
        "mensaje":    f"{resultado['insertados']} secciones insertadas correctamente",
        "insertados": resultado["insertados"],
        "errores":    resultado["errores"]
    }
