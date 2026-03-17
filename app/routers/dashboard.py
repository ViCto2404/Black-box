from fastapi import APIRouter, Query
from app.services import analisis

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/resumen/{periodo}")
def resumen_periodo(periodo:str):
    return analisis.get_resumen_periodo(periodo)

@router.get("/rendimiento/{periodo}")
def rendimiento_materias(
    periodo:str,
    carrera: str = Query(defaul=None)
):
    return analisis.get_rendimiento_por_materia(periodo, carrera)

@router.get("/criticas/{periodo}")
def materias_criticas(
    periodo: str,
    umbral: float = Query(default=30.0)
):
    return analisis.get_materias_criticas(periodo, umbral)

@router.get("/masa-estudiantil")
def masa_estudiantil(
    carrera: str = Query(default=None)
):
    return analisis.get_masa_estudiantil(carrera)

@router.get("/debug/{periodo}")
def debug(periodo: str):
    from app.database.supabase_client import supabase

    # Prueba 1: trae calificaciones sin join
    cal = supabase.table("calificacion") \
        .select("*") \
        .eq("periodo_academico", periodo) \
        .execute()

    # Prueba 2: trae calificaciones con join
    cal_join = supabase.table("calificacion") \
        .select("*, materia(codigo, nombre, codigo_carrera)") \
        .eq("periodo_academico", periodo) \
        .execute()

    return {
        "sin_join": cal.data,
        "con_join": cal_join.data
    }

@router.get("/debug-config")
def debug_config():
    import os
    from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
    return {
        "url": SUPABASE_URL,
        "key_primeros_30": SUPABASE_SERVICE_KEY[:30] if SUPABASE_SERVICE_KEY else None,
        "key_es_none": SUPABASE_SERVICE_KEY is None
    }