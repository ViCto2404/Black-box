from app.database.supabase_client import supabase

def get_todos_directores(codigo_escuela: str = None):
    try:
        # Especificar la relación para evitar ambigüedad (usamos la que vincula codigo_escuela)
        relacion = "escuelas!directores_codigo_escuela_fkey(nombre)"
        query = supabase.table("directores").select(f"*, {relacion}")
        
        if codigo_escuela:
            query = query.eq("codigo_escuela", codigo_escuela)
        
        res = query.execute()
        data = res.data if res.data else []
            
        for d in data:
            # PostgREST devuelve la llave con el nombre de la relación especificada
            escuela_info = d.get("escuelas") # A veces lo simplifica si no hay conflicto, pero veamos
            if not escuela_info:
                # Intentar con el nombre completo de la relación si no está en 'escuelas'
                escuela_info = d.get("escuelas!directores_codigo_escuela_fkey")

            if escuela_info:
                d["nombre_escuela"] = escuela_info.get("nombre", "N/A")
            else:
                d["nombre_escuela"] = "Sin Escuela"
            
            # Limpiar llaves de join
            d.pop("escuelas", None)
            d.pop("escuelas!directores_codigo_escuela_fkey", None)
                
        return data
    except Exception as e:
        print(f"ERROR en get_todos_directores: {str(e)}")
        return []

def get_director_por_id(id_unphu: str):
    try:
        data = supabase.table("directores").select("*").eq("id_unphu", id_unphu).execute()
        return data.data[0] if data.data else None
    except:
        return None

def crear_director(payload: dict):
    try:
        # 1. Insertar en tabla directores
        data = supabase.table("directores").insert(payload).execute()
        if not data.data:
            return None, "No se pudo insertar el registro en la base de datos"

        # 2. Crear usuario de autenticación
        # Usamos try/except por si el correo ya existe en Auth
        try:
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
        except Exception as auth_err:
            print(f"Aviso: No se creó usuario auth (puede que ya exista): {str(auth_err)}")
            
        return data.data[0], None
    except Exception as e:
        return None, str(e)

def actualizar_director(id_unphu: str, payload: dict):
    try:
        payload_limpio = {k: v for k, v in payload.items() if v is not None}
        # Asegurarnos de que el ID se mantenga consistente
        data = supabase.table("directores").update(payload_limpio).eq("id_unphu", id_unphu).execute()
        
        if not data.data:
            return None, f"No se encontró el director con ID {id_unphu} para actualizar"
            
        return data.data[0], None
    except Exception as e:
        return None, str(e)

def eliminar_director(id_unphu: str):
    try:
        res = supabase.table("directores").delete().eq("id_unphu", id_unphu).execute()
        if not res.data:
             return False, "No se encontró el registro para eliminar"
        return True, None
    except Exception as e:
        return False, str(e)
