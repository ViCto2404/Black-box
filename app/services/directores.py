from app.database.supabase_client import supabase

def get_todos_directores(codigo_escuela: str = None):
    try:
        # Intento 1: Tabla 'directores'
        query = supabase.table("directores").select("*")
        if codigo_escuela:
            query = query.eq("codigo_escuela", codigo_escuela)
        
        data = query.execute()
        
        # Si no hay datos, intentamos con 'director' (singular)
        if not data.data:
            print("DEBUG: Tabla 'directores' vacía, intentando con 'director'...")
            query_alt = supabase.table("director").select("*")
            if codigo_escuela:
                query_alt = query_alt.eq("codigo_escuela", codigo_escuela)
            data = query_alt.execute()

        if not data.data:
            return []
            
        # Intentar traer el nombre de la escuela si existe la relación
        # Lo haremos de forma segura para no romper la respuesta
        for d in data.data:
            if "codigo_escuela" in d and d["codigo_escuela"]:
                try:
                    escuela = supabase.table("escuelas").select("nombre").eq("codigo", d["codigo_escuela"]).single().execute()
                    d["nombre_escuela"] = escuela.data["nombre"] if escuela.data else "N/A"
                except:
                    d["nombre_escuela"] = "N/A"
            else:
                d["nombre_escuela"] = "Sin Escuela"
                
        return data.data
    except Exception as e:
        print(f"ERROR en get_todos_directores: {str(e)}")
        return []

def get_director_por_id(id_unphu: str):
    # Intentar en ambas tablas
    for tabla in ["directores", "director"]:
        try:
            data = supabase.table(tabla).select("*").eq("id_unphu", id_unphu).execute()
            if data.data:
                return data.data[0]
        except:
            continue
    return None

def crear_director(payload: dict):
    try:
        # Intentar insertar en 'directores'
        data = supabase.table("directores").insert(payload).execute()
        
        # Registrar en profiles
        auth_user = supabase.auth.admin.create_user({
            "email": payload["correo_institucional"],
            "password": payload["id_unphu"],
            "email_confirm": True
        })
        
        if auth_user.user:
            supabase.table("profiles").insert({
                "id": auth_user.user.id,
                "id_unphu": payload["id_unphu"],
                "rol": "director"
            }).execute()
            
        return data.data[0] if data.data else None, None
    except Exception as e:
        return None, str(e)

def actualizar_director(id_unphu: str, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        data = supabase.table("directores").update(payload_limpio).eq("id_unphu", id_unphu).execute()
        return data.data[0] if data.data else None, None
    except Exception as e:
        return None, str(e)

def eliminar_director(id_unphu: str):
    try:
        supabase.table("directores").delete().eq("id_unphu", id_unphu).execute()
        return True, None
    except Exception as e:
        return False, str(e)
