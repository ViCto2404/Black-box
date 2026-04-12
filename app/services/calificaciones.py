import pandas as pd
from io import BytesIO
from app.database.supabase_client import supabase


def get_calificaciones(periodo: str = None, id_estudiante: str = None, codigo_materia: str = None, id_seccion: int = None):
    query = supabase.table("calificacion") \
        .select("id, id_estudiante, codigo_materia, id_seccion, nota, periodo_academico")

    if periodo:
        query = query.eq("periodo_academico", periodo)
    if id_estudiante:
        query = query.eq("id_estudiante", id_estudiante)
    if codigo_materia:
        query = query.eq("codigo_materia", codigo_materia)
    if id_seccion:
        query = query.eq("id_seccion", id_seccion)

    data = query.execute()
    if not data.data:
        return []

    df = pd.DataFrame(data.data)

    # Traer nombres de materias
    materias = supabase.table("materia").select("codigo, nombre").execute()
    if materias.data:
        df_materias = pd.DataFrame(materias.data) \
            .rename(columns={"codigo": "codigo_materia", "nombre": "nombre_materia"})
        df = df.merge(df_materias, on="codigo_materia", how="left")

    # Traer info de secciones
    secciones = supabase.table("seccion") \
        .select("id, codigo_seccion, periodo") \
        .execute()
    if secciones.data:
        df_secciones = pd.DataFrame(secciones.data) \
            .rename(columns={"id": "id_seccion"})
        df = df.merge(df_secciones, on="id_seccion", how="left")

    return df.to_dict(orient="records")


def crear_calificacion(payload: dict):
    try:
        # Verificar que la sección existe
        seccion = supabase.table("seccion") \
            .select("id, materia, periodo") \
            .eq("id", payload["id_seccion"]) \
            .execute()
        if not seccion.data:
            return None, f"La sección '{payload['id_seccion']}' no existe"

        sec = seccion.data[0]

        # Verificar que la materia de la sección coincide
        if sec["materia"] != payload["codigo_materia"]:
            return None, f"La sección '{payload['id_seccion']}' no corresponde a la materia '{payload['codigo_materia']}'"

        # Verificar que el periodo coincide
        if sec["periodo"] != payload["periodo_academico"]:
            return None, f"El periodo '{payload['periodo_academico']}' no coincide con el periodo de la sección '{sec['periodo']}'"

        # Verificar duplicado
        existente = supabase.table("calificacion") \
            .select("id") \
            .eq("id_estudiante",     payload["id_estudiante"]) \
            .eq("codigo_materia",    payload["codigo_materia"]) \
            .eq("id_seccion",        payload["id_seccion"]) \
            .eq("periodo_academico", payload["periodo_academico"]) \
            .execute()
        if existente.data:
            return None, "Ya existe una calificación para este estudiante en esta sección y periodo"

        data = supabase.table("calificacion").insert(payload).execute()
        if not data.data:
            return None, "Error al crear la calificación"
        return data.data[0], None

    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def actualizar_calificacion(id: int, nota: float):
    if not 0 <= nota <= 100:
        return None, "La nota debe estar entre 0 y 100"

    data = supabase.table("calificacion") \
        .update({"nota": nota}) \
        .eq("id", id) \
        .execute()

    if not data.data:
        return None, "Calificación no encontrada"
    return data.data[0], None


def eliminar_calificacion(id: int):
    data = supabase.table("calificacion") \
        .delete() \
        .eq("id", id) \
        .execute()

    if not data.data:
        return False, "Calificación no encontrada"
    return True, None


def carga_masiva(registros: list):
    if not registros:
        return {"insertados": 0, "errores": []}

    errores = []
    insertados = 0

    for r in registros:
        # Verificar sección
        seccion = supabase.table("seccion") \
            .select("id, materia, periodo") \
            .eq("id", r["id_seccion"]) \
            .execute()

        if not seccion.data:
            errores.append(f"Sección {r['id_seccion']} no existe — estudiante {r['id_estudiante']}")
            continue

        sec = seccion.data[0]
        if sec["materia"] != r["codigo_materia"]:
            errores.append(f"Sección {r['id_seccion']} no corresponde a materia {r['codigo_materia']}")
            continue

        if sec["periodo"] != r["periodo_academico"]:
            errores.append(f"Periodo {r['periodo_academico']} no coincide con el periodo de la sección {sec['periodo']}")
            continue

        existente = supabase.table("calificacion") \
            .select("id") \
            .eq("id_estudiante",     r["id_estudiante"]) \
            .eq("codigo_materia",    r["codigo_materia"]) \
            .eq("id_seccion",        r["id_seccion"]) \
            .eq("periodo_academico", r["periodo_academico"]) \
            .execute()

        if existente.data:
            errores.append(f"Duplicado: {r['id_estudiante']} — {r['codigo_materia']} — sección {r['id_seccion']}")
            continue

        resultado = supabase.table("calificacion").insert(r).execute()
        if resultado.data:
            insertados += 1
        else:
            errores.append(f"Error al insertar: {r['id_estudiante']} — {r['codigo_materia']}")

    return {"insertados": insertados, "errores": errores}


def generar_plantilla_excel():
    columnas = ["id_estudiante", "codigo_materia", "id_seccion", "nota", "periodo_academico"]
    # Crear un DataFrame vacío con las columnas
    df = pd.DataFrame(columns=columnas)
    
    # Agregar una fila de ejemplo
    ejemplo = {
        "id_estudiante": "20-0001",
        "codigo_materia": "INF-101",
        "id_seccion": 1,
        "nota": 85.5,
        "periodo_academico": "2024-1"
    }
    df.loc[0] = ejemplo

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla')
    
    return output.getvalue()
