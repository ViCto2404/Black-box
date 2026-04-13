from app.database.supabase_client import supabase


def get_todas_escuelas(estado: str = None):
    # La relación se llama 'directores' si así está en Supabase, o usamos el nombre de la columna
    # Probaremos con el nombre de la columna id_director para el join
    query = supabase.table("escuelas").select("*, directores:id_director(nombre)")
    if estado:
        query = query.eq("estado", estado)
    
    data = query.execute()
    if not data.data:
        return []
    
    resultados = []
    for e in data.data:
        # Ajustamos el mapeo según la respuesta del join
        e["nombre_director"] = e["directores"]["nombre"] if isinstance(e.get("directores"), dict) else "Sin Director"
        e.pop("directores", None)
        resultados.append(e)
    return resultados


def get_escuela_por_codigo(codigo: str):
    data = supabase.table("escuelas") \
        .select("*, directores:id_director(nombre)") \
        .eq("codigo", codigo) \
        .single() \
        .execute()
    
    if not data.data:
        return None
    
    e = data.data
    e["nombre_director"] = e["directores"]["nombre"] if isinstance(e.get("directores"), dict) else "Sin Director"
    e.pop("directores", None)
    return e


def crear_escuela(payload: dict):
    try:
        # Verificar que el código de escuela no exista
        existente = supabase.table("escuelas") \
            .select("codigo") \
            .eq("codigo", payload["codigo"]) \
            .execute()
        if existente.data:
            return None, "Ya existe una escuela con ese código"

        # Verificar que el director existe
        id_dir = payload.get("id_director")
        if id_dir:
            director = supabase.table("directores") \
                .select("id_unphu") \
                .eq("id_unphu", id_dir) \
                .execute()
            if not director.data:
                return None, f"El director '{id_dir}' no existe"

        # Insertar escuela
        data = supabase.table("escuelas").insert(payload).execute()
        if not data.data:
            return None, "Error al crear la escuela"
        
        # Sincronizar: Actualizar al director con su nueva escuela
        if id_dir:
            supabase.table("directores").update({"codigo_escuela": payload["codigo"]}).eq("id_unphu", id_dir).execute()

        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def actualizar_escuela(codigo: str, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        if not payload_limpio:
            return None, "No hay campos para actualizar"
        
        # Si se está cambiando el director
        nuevo_id_dir = payload_limpio.get("id_director")
        if nuevo_id_dir:
            # 1. Verificar que el nuevo director exista
            director_res = supabase.table("directores").select("id_unphu").eq("id_unphu", nuevo_id_dir).execute()
            if not director_res.data:
                return None, f"El director '{nuevo_id_dir}' no existe"

            # 2. Obtener el director actual de esta escuela para "liberarlo"
            escuela_actual = supabase.table("escuelas").select("id_director").eq("codigo", codigo).single().execute()
            if escuela_actual.data and escuela_actual.data["id_director"]:
                id_dir_anterior = escuela_actual.data["id_director"]
                # Limpiar la escuela del director anterior
                supabase.table("directores").update({"codigo_escuela": None}).eq("id_unphu", id_dir_anterior).execute()

        # 3. Actualizar la escuela
        data = supabase.table("escuelas").update(payload_limpio).eq("codigo", codigo).execute()
        if not data.data:
            return None, "Escuela no encontrada"

        # 4. Sincronizar al nuevo director
        if nuevo_id_dir:
            supabase.table("directores").update({"codigo_escuela": codigo}).eq("id_unphu", nuevo_id_dir).execute()

        return data.data[0], None
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def eliminar_escuela(codigo: str):
    try:
        data = supabase.table("escuelas") \
            .delete() \
            .eq("codigo", codigo) \
            .execute()
        if not data.data:
            return False, "Escuela no encontrada"
        return True, None
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"
