from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from app.services import exportacion
from datetime import datetime
from typing import Literal, Optional
from io import BytesIO

router = APIRouter(prefix="/reportes", tags=["Reportes"])

def generar_respuesta(contenido: bytes, nombre_base: str, formato: str, periodo: Optional[str] = None):
    timestamp = datetime.now().strftime('%Y%m%d')
    # Limpiamos el periodo para el nombre del archivo
    periodo_clean = str(periodo).replace(" ", "_") if periodo else ""
    suffix = f"_{periodo_clean}" if periodo_clean else ""
    
    if formato == "excel":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        nombre = f"{nombre_base}{suffix}_{timestamp}.xlsx"
    else:
        media_type = "application/pdf"
        nombre = f"{nombre_base}{suffix}_{timestamp}.pdf"
    
    # Usamos StreamingResponse para una mejor compatibilidad con descargas binarias
    return StreamingResponse(
        BytesIO(contenido),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

# Metadatos para Swagger UI
RESPONSES_METADATA = {
    200: {
        "content": {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                "schema": {"type": "string", "format": "binary"}
            },
            "application/pdf": {
                "schema": {"type": "string", "format": "binary"}
            }
        },
        "description": "Retorna el archivo binario para su descarga.",
    }
}

@router.get("/resumen/{periodo}", responses=RESPONSES_METADATA)
def reporte_resumen(periodo: str, format: Literal["excel", "pdf"] = Query("excel")):
    try:
        if format == "excel":
            contenido = exportacion.exportar_resumen_periodo_excel(periodo)
        else:
            contenido = exportacion.exportar_resumen_periodo_pdf(periodo)
        return generar_respuesta(contenido, "resumen_academico", format, periodo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rendimiento/{periodo}", responses=RESPONSES_METADATA)
def reporte_rendimiento(periodo: str, format: Literal["excel", "pdf"] = Query("excel")):
    try:
        if format == "excel":
            contenido = exportacion.exportar_rendimiento_excel(periodo)
        else:
            contenido = exportacion.exportar_rendimiento_pdf(periodo)
        return generar_respuesta(contenido, "rendimiento_asignaturas", format, periodo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/criticas/{periodo}", responses=RESPONSES_METADATA)
def reporte_criticas(periodo: str, format: Literal["excel", "pdf"] = Query("excel")):
    try:
        if format == "excel":
            contenido = exportacion.exportar_materias_criticas_excel(periodo)
        else:
            contenido = exportacion.exportar_materias_criticas_pdf(periodo)
        return generar_respuesta(contenido, "materias_criticas", format, periodo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/masa/{periodo}", responses=RESPONSES_METADATA)
def reporte_masa(periodo: str, format: Literal["excel", "pdf"] = Query("excel")):
    try:
        if format == "excel":
            contenido = exportacion.exportar_masa_estudiantil_excel(periodo)
        else:
            contenido = exportacion.exportar_masa_estudiantil_pdf(periodo)
        return generar_respuesta(contenido, "masa_estudiantil", format, periodo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materia/{codigo_materia}/{periodo}", responses=RESPONSES_METADATA)
def reporte_materia_detalle(codigo_materia: str, periodo: str, format: Literal["excel", "pdf"] = Query("excel")):
    try:
        if format == "excel":
            contenido = exportacion.exportar_materia_detalle_excel(codigo_materia, periodo)
        else:
            contenido = exportacion.exportar_materia_detalle_pdf(codigo_materia, periodo)
        return generar_respuesta(contenido, f"detalle_materia_{codigo_materia}", format, periodo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback", responses=RESPONSES_METADATA)
def reporte_feedback(codigo_carrera: Optional[str] = Query(None), format: Literal["excel", "pdf"] = Query("excel")):
    try:
        if format == "excel":
            contenido = exportacion.exportar_feedback_excel(codigo_carrera)
        else:
            contenido = exportacion.exportar_feedback_pdf(codigo_carrera)
        return generar_respuesta(contenido, "feedback_estudiantil", format, codigo_carrera)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
