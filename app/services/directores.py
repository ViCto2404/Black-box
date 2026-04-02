from app.database.supabase_client import supabase


def _verificar_conflicto_rol(id_unphu: str):
    # Un director no puede ser estudiante al mismo tiempo
    estudiante = supabase.table("estudiantes") \
        .select("id_unphu") \
        .eq("id_unphu", id_unphu) \
        .execute()
    if estudiante.data:
        return "Este ID ya pertenece a un estudiante. Un usuario no puede ser director y estudiante a la vez"

    # Un director puede ser profesor también — no hay conflicto
    return None


def get_todos_directores(codigo_escuela: str = None):
    query = supabase.table("directores") \
        .select("*, carrera:codigo_escuela(nombre)")
    if codigo_escuela:
        query = query.eq("codigo_escuela", codigo_escuela)
    data = query.execute()
    if not data.data:
        return []
    resultados = []
    for d in data.data:
        d["nombre_escuela"] = d["carrera"]["nombre"] if isinstance(d.get("carrera"), dict) else None
        d.pop("carrera", None)
        resultados.append(d)
    return resultados


def get_director_por_id(id_unphu: str):
    data = supabase.table("directores") \
        .select("*") \
        .eq("id_unphu", id_unphu) \
        .single() \
        .execute()
    return data.data if data.data else None


def crear_director(payload: dict):
    try:
        # Verificar conflicto de rol
        error_rol = _verificar_conflicto_rol(payload["id_unphu"])
        if error_rol:
            return None, error_rol

        existente = supabase.table("directores") \
            .select("id_unphu") \
            .eq("id_unphu", payload["id_unphu"]) \
            .execute()
        if existente.data:
            return None, "Ya existe un director con ese ID"

        correo = supabase.table("directores") \
            .select("correo_institucional") \
            .eq("correo_institucional", payload["correo_institucional"]) \
            .execute()
        if correo.data:
            return None, "El correo institucional ya está en uso"

        if payload.get("codigo_escuela"):
            escuela = supabase.table("escuela") \
                .select("codigo") \
                .eq("codigo", payload["codigo_escuela"]) \
                .execute()
            if not escuela.data:
                return None, f"La escuela '{payload['codigo_escuela']}' no existe"

        # Crear usuario en Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email":    payload["correo_institucional"],
            "password": payload["id_unphu"],  # contraseña temporal = id_unphu
            "email_confirm": True
        })

        if not auth_response.user:
            return None, "Error al crear el usuario de autenticación"

        user_id = auth_response.user.id

        # Insertar en la tabla director
        data = supabase.table("directores").insert(payload).execute()
        if not data.data:
            return None, "Error al crear el director"

        # Registrar en profiles
        supabase.table("profiles").insert({
            "id":       user_id,
            "id_unphu": payload["id_unphu"],
            "rol":      "director"
        }).execute()

        return {
            **data.data[0],
            "mensaje": f"Usuario creado. Contraseña temporal: {payload['id_unphu']}"
        }, None

    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def actualizar_director(id_unphu: str, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        if not payload_limpio:
            return None, "No hay campos para actualizar"

        # Verificar que la escuela existe si se está actualizando
        if payload_limpio.get("codigo_escuela"):
            escuela = supabase.table("escuelas") \
                .select("codigo") \
                .eq("codigo", payload_limpio["codigo_escuela"]) \
                .execute()
            if not escuela.data:
                return None, f"La escuela '{payload_limpio['codigo_escuela']}' no existe"

        data = supabase.table("directores") \
            .update(payload_limpio) \
            .eq("id_unphu", id_unphu) \
            .execute()
        if not data.data:
            return None, "Director no encontrado"
        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def eliminar_director(id_unphu: str):
    try:
        # Verificar que no tenga una escuela asignada antes de eliminar
        escuela = supabase.table("escuelas") \
            .select("codigo") \
            .eq("id_director", id_unphu) \
            .execute()
        if escuela.data:
            return False, "No se puede eliminar un director que tiene una escuela asignada. Reasigna el director primero"

        data = supabase.table("directores") \
            .delete() \
            .eq("id_unphu", id_unphu) \
            .execute()
        if not data.data:
            return False, "Director no encontrado"
        return True, None
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"