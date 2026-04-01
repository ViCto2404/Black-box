from app.database.supabase_client import supabase


def get_todas_carreras(estado: str = None, codigo_escuela: str = None):
    query = supabase.table("carreras").select("*, escuelas(nombre)")
    if estado:
        query = query.eq("estado", estado)
    if codigo_escuela:
        query = query.eq("codigo_escuela", codigo_escuela)
    data = query.execute()
    if not data.data:
        return []
    resultados = []
    for c in data.data:
        c["nombre_escuela"] = c["escuelas"]["nombre"] if isinstance(c.get("escuelas"), dict) else None
        c.pop("escuelas", None)
        resultados.append(c)
    return resultados


def get_carrera_por_codigo(codigo: str):
    data = supabase.table("carreras") \
        .select("*, escuelas(nombre)") \
        .eq("codigo", codigo) \
        .single() \
        .execute()
    if not data.data:
        return None
    c = data.data
    c["nombre_escuela"] = c["escuelas"]["nombre"] if isinstance(c.get("escuelas"), dict) else None
    c.pop("escuelas", None)
    return c


def crear_carrera(payload: dict):
    try:
        existente = supabase.table("carreras") \
            .select("codigo") \
            .eq("codigo", payload["codigo"]) \
            .execute()
        if existente.data:
            return None, "Ya existe una carrera con ese código"

        escuela = supabase.table("escuelas") \
            .select("codigo") \
            .eq("codigo", payload["codigo_escuela"]) \
            .execute()
        if not escuela.data:
            return None, f"La escuela '{payload['codigo_escuela']}' no existe"

        data = supabase.table("carreras").insert(payload).execute()
        if not data.data:
            return None, "Error al crear la carrera"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def actualizar_carrera(codigo: str, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        if not payload_limpio:
            return None, "No hay campos para actualizar"

        if payload_limpio.get("codigo_escuela"):
            escuela = supabase.table("escuelas") \
                .select("codigo") \
                .eq("codigo", payload_limpio["codigo_escuela"]) \
                .execute()
            if not escuela.data:
                return None, f"La escuela '{payload_limpio['codigo_escuela']}' no existe"

        data = supabase.table("carreras") \
            .update(payload_limpio) \
            .eq("codigo", codigo) \
            .execute()
        if not data.data:
            return None, "Carrera no encontrada"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def eliminar_carrera(codigo: str):
    try:
        # Verificar que no tenga estudiantes o materias activas
        estudiantes = supabase.table("estudiantes") \
            .select("id_unphu") \
            .eq("codigo_carrera", codigo) \
            .eq("estado_activo", "Activo") \
            .execute()
        if estudiantes.data:
            return False, "No se puede eliminar una carrera con estudiantes activos"

        materias = supabase.table("materia") \
            .select("codigo") \
            .eq("codigo_carrera", codigo) \
            .eq("estado", "Activa") \
            .execute()
        if materias.data:
            return False, "No se puede eliminar una carrera con materias activas"

        data = supabase.table("carreras") \
            .delete() \
            .eq("codigo", codigo) \
            .execute()
        if not data.data:
            return False, "Carrera no encontrada"
        return True, None
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"