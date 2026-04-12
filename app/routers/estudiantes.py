from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Response
from typing import Annotated
from app.services import estudiantes as svc
from app.services.validacion import procesar_archivo_estudiantes
from app.models.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponde

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

@router.get("/plantilla")
def descargar_plantilla():
    contenido = svc.generar_plantilla_estudiante()
    return Response(
        content=contenido,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=plantilla_estudiantes.xlsx"}
    )

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

    registros, errores_validacion = procesar_archivo_estudiantes(contenido, archivo.filename)

    if errores_validacion:
        raise HTTPException(
            status_code=422,
            detail={
                "mensaje": "El archivo contiene errores de validación",
                "errores": errores_validacion
            }
        )

    resultado = svc.carga_masiva_estudiantes(registros)
    return {
        "mensaje":    f"{resultado['insertados']} estudiantes procesados correctamente",
        "insertados": resultado["insertados"],
        "errores":    resultado["errores"]
    }
