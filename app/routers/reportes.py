from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.services.exportacion import exportar_excel, exportar_pdf
from datetime import datetime

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/excel/{periodo}")
def descargar_excel(periodo: str):
    try:
        contenido = exportar_excel(periodo)
        nombre    = f"reporte_academico_{periodo}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return Response(
            content=contenido,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={nombre}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/{periodo}")
def descargar_pdf(periodo: str):
    try:
        contenido = exportar_pdf(periodo)
        nombre    = f"reporte_academico_{periodo}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return Response(
            content=contenido,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nombre}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))