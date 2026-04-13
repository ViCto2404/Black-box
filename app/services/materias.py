from app.database.supabase_client import supabase


def get_todas_materias(estado: str = None, codigo_carrera: str = None, codigo_escuela: str = None):
    # Si filtramos por escuela, necesitamos el join con carreras
    if codigo_escuela:
        query = supabase.table("materia").select("*, carreras!inner(codigo_escuela)")
        query = query.eq("carreras.codigo_escuela", codigo_escuela)
    else:
        query = supabase.table("materia").select("*")
        
    if estado:
        query = query.eq("estado", estado)
    if codigo_carrera:
        query = query.eq("codigo_carrera", codigo_carrera)
        
    data = query.execute()
    return data.data if data.data else []


def get_materia_por_codigo(codigo: str):
    data = supabase.table("materia") \
        .select("*") \
        .eq("codigo", codigo) \
        .single() \
        .execute()
    return data.data if data.data else None


def crear_materia(payload: dict):
    try:
        existente = supabase.table("materia") \
            .select("codigo") \
            .eq("codigo", payload["codigo"]) \
            .execute()
        if existente.data:
            return None, "Ya existe una materia con ese código"

        # Verificar que la carrera existe
        carrera = supabase.table("carreras") \
            .select("codigo") \
            .eq("codigo", payload["codigo_carrera"]) \
            .execute()
        if not carrera.data:
            return None, f"La carrera '{payload['codigo_carrera']}' no existe"

        # Verificar que el profesor existe si se provee
        if payload.get("id_profesor"):
            profesor = supabase.table("profesor") \
                .select("id_profesor") \
                .eq("id_profesor", payload["id_profesor"]) \
                .execute()
            if not profesor.data:
                return None, f"El profesor '{payload['id_profesor']}' no existe"

        data = supabase.table("materia").insert(payload).execute()
        if not data.data:
            return None, "Error al crear la materia"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def actualizar_materia(codigo: str, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        if not payload_limpio:
            return None, "No hay campos para actualizar"
        data = supabase.table("materia") \
            .update(payload_limpio) \
            .eq("codigo", codigo) \
            .execute()
        if not data.data:
            return None, "Materia no encontrada"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def eliminar_materia(codigo: str):
    try:
        data = supabase.table("materia") \
            .delete() \
            .eq("codigo", codigo) \
            .execute()
        if not data.data:
            return False, "Materia no encontrada"
        return True, None
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"