from app.database.supabase_client import supabase
import pandas as pd
from io import BytesIO


def get_todas_secciones(periodo: str = None, materia: str = None, estado: str = None):
    query = supabase.table("seccion").select("*")
    if periodo:
        query = query.eq("periodo", periodo)
    if materia:
        query = query.eq("materia", materia)
    if estado:
        query = query.eq("estado", estado)
    data = query.execute()
    return data.data if data.data else []


def get_seccion_por_id(id: int):
    data = supabase.table("seccion") \
        .select("*") \
        .eq("id", id) \
        .single() \
        .execute()
    return data.data if data.data else None


def crear_seccion(payload: dict):
    try:
        # Verificar que la materia existe
        materia = supabase.table("materia") \
            .select("codigo") \
            .eq("codigo", payload["materia"]) \
            .execute()
        if not materia.data:
            return None, f"La materia '{payload['materia']}' no existe"

        # Verificar que el profesor existe si se provee
        if payload.get("profesor"):
            profesor = supabase.table("profesor") \
                .select("id_profesor") \
                .eq("id_profesor", payload["profesor"]) \
                .execute()
            if not profesor.data:
                return None, f"El profesor '{payload['profesor']}' no existe"

        # Verificar que no exista la misma sección en el mismo periodo
        existente = supabase.table("seccion") \
            .select("id") \
            .eq("codigo_seccion", payload["codigo_seccion"]) \
            .eq("materia",        payload["materia"]) \
            .eq("periodo",        payload["periodo"]) \
            .execute()
        if existente.data:
            return None, "Ya existe una sección con ese código para esta materia y periodo"

        data = supabase.table("seccion").insert(payload).execute()
        if not data.data:
            return None, "Error al crear la sección"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def actualizar_seccion(id: int, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        if not payload_limpio:
            return None, "No hay campos para actualizar"
        data = supabase.table("seccion") \
            .update(payload_limpio) \
            .eq("id", id) \
            .execute()
        if not data.data:
            return None, "Sección no encontrada"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def eliminar_seccion(id: int):
    try:
        data = supabase.table("seccion") \
            .delete() \
            .eq("id", id) \
            .execute()
        if not data.data:
            return False, "Sección no encontrada"
        return True, None
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"


def carga_masiva_secciones(registros: list):
    if not registros:
        return {"insertados": 0, "errores": []}

    errores = []
    insertados = 0

    for r in registros:
        # Verificar duplicado
        existente = supabase.table("seccion") \
            .select("id") \
            .eq("codigo_seccion", r["codigo_seccion"]) \
            .eq("materia",        r["materia"]) \
            .eq("periodo",        r["periodo"]) \
            .execute()

        if existente.data:
            errores.append(f"Duplicado: {r['codigo_seccion']} — {r['materia']} ({r['periodo']})")
            continue

        resultado = supabase.table("seccion").insert(r).execute()
        if resultado.data:
            insertados += 1
        else:
            errores.append(f"Error al insertar: {r['codigo_seccion']} — {r['materia']}")

    return {"insertados": insertados, "errores": errores}


def generar_plantilla_seccion():
    columnas = ["codigo_seccion", "materia", "profesor", "periodo", "aula", "cupo_max", "horario", "estado"]
    df = pd.DataFrame(columns=columnas)

    ejemplo = {
        "codigo_seccion": "001",
        "materia": "INF-101",
        "profesor": "PROF-001",
        "periodo": "2024-1",
        "aula": "A-101",
        "cupo_max": 30,
        "horario": "Lun/Mie 08:00-10:00",
        "estado": "Activa"
    }
    df.loc[0] = ejemplo

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla Secciones')

    return output.getvalue()
