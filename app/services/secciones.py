from app.database.supabase_client import supabase


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