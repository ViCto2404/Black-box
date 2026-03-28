from app.database.supabase_client import supabase


def _verificar_rol_conflicto(id_profesor: str):
    # Un profesor no puede ser estudiante al mismo tiempo
    estudiante = supabase.table("estudiantes") \
        .select("id_unphu") \
        .eq("id_unphu", id_profesor) \
        .execute()
    if estudiante.data:
        return "Este ID ya pertenece a un estudiante. Un usuario no puede ser profesor y estudiante a la vez"
    return None


def get_todos_profesores(estado: str = None, codigo_carrera: str = None):
    query = supabase.table("profesor").select("*, codigo_carrera(nombre)")
    if estado:
        query = query.eq("estado", estado)
    if codigo_carrera:
        query = query.eq("codigo_carrera", codigo_carrera)
    data = query.execute()
    if not data.data:
        return []
    resultados = []
    for p in data.data:
        p["nombre_carrera"] = p["carrera"]["nombre"] if isinstance(p.get("carrera"), dict) else None
        p.pop("carrera", None)
        resultados.append(p)
    return resultados


def get_profesor_por_id(id_profesor: str):
    data = supabase.table("profesor") \
        .select("*, codigo_carrera(nombre)") \
        .eq("id_profesor", id_profesor) \
        .single() \
        .execute()
    if not data.data:
        return None
    p = data.data
    p["nombre_carrera"] = p["codigo_carrera"]["nombre"] if isinstance(p.get("codigo_carrera"), dict) else None
    p.pop("codigo_carrera", None)
    return p


def crear_profesor(payload: dict):
    try:
        # Verificar conflicto de rol
        error_rol = _verificar_rol_conflicto(payload["id_profesor"])
        if error_rol:
            return None, error_rol

        existente = supabase.table("profesor") \
            .select("id_profesor") \
            .eq("id_profesor", payload["id_profesor"]) \
            .execute()
        if existente.data:
            return None, "Ya existe un profesor con ese ID"

        data = supabase.table("profesor").insert(payload).execute()
        if not data.data:
            return None, "Error al crear el profesor"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def actualizar_profesor(id_profesor: str, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        if not payload_limpio:
            return None, "No hay campos para actualizar"
        data = supabase.table("profesor") \
            .update(payload_limpio) \
            .eq("id_profesor", id_profesor) \
            .execute()
        if not data.data:
            return None, "Profesor no encontrado"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def eliminar_profesor(id_profesor: str):
    try:
        data = supabase.table("profesor") \
            .delete() \
            .eq("id_profesor", id_profesor) \
            .execute()
        if not data.data:
            return False, "Profesor no encontrado"
        return True, None
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"