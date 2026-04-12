from app.database.supabase_client import supabase
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

def login(email: str, password: str):
    try:
        # IMPORTANTE: Creamos un cliente temporal solo para validar la contraseña.
        # Esto evita que el cliente global 'supabase' se contamine con la sesión del usuario.
        auth_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        response = auth_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not response.user:
            return None, "Credenciales incorrectas"

        user_id = response.user.id
        access_token = response.session.access_token

        # 1. Obtener el perfil básico usando el cliente global (Service Role)
        perfil = supabase.table("profiles") \
            .select("rol, id_unphu") \
            .eq("id", user_id) \
            .single() \
            .execute()

        if not perfil.data:
            return None, "El usuario no tiene un perfil asignado en el sistema"

        rol_raw = str(perfil.data["rol"]).lower().strip()
        id_unphu_raw = str(perfil.data["id_unphu"]).strip()

        nombre = "Usuario"
        codigo_escuela = None
        codigo_carrera = None
        estado = "Activo"

        # 2. Obtener datos específicos según el rol (siempre usando el cliente global)
        if rol_raw == "estudiante":
            res = supabase.table("estudiantes").select("nombre, codigo_carrera, estado_activo").eq("id_unphu", id_unphu_raw).execute()
            if res.data:
                nombre = res.data[0].get("nombre", "Estudiante")
                codigo_carrera = res.data[0].get("codigo_carrera")
                estado = res.data[0].get("estado_activo", "Activo")
        
        elif rol_raw == "director":
            res = supabase.table("directores").select("*").eq("correo_institucional", email).execute()
            if not res.data:
                res = supabase.table("directores").select("*").eq("id_unphu", id_unphu_raw).execute()

            if res.data:
                director = res.data[0]
                nombre = director.get("nombre", "Director")
                codigo_escuela = director.get("codigo_escuela")
                # Si no tiene escuela, lo manejamos en el frontend
        
        elif rol_raw == "profesor":
            res = supabase.table("profesor").select("nombre").eq("correo_institucional", email).execute()
            if res.data:
                nombre = res.data[0].get("nombre", "Profesor")

        elif rol_raw == "administrador":
            nombre = "Administrador"

        return {
            "access_token": access_token,
            "token_type":   "bearer",
            "rol":          rol_raw,
            "id_unphu":     id_unphu_raw,
            "nombre":       nombre,
            "codigo_escuela": codigo_escuela,
            "codigo_carrera": codigo_carrera,
            "estado":       estado
        }, None

    except Exception as e:
        print(f"ERROR LOGIN: {str(e)}")
        return None, "Credenciales incorrectas"


def logout(token: str):
    try:
        # Para el logout, usamos un cliente temporal para no afectar el global
        temp_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        temp_client.auth.sign_out()
        return True, None
    except Exception as e:
        return False, str(e)
    
def cambiar_contrasena(email: str, password_actual: str, password_nuevo: str, password_confirmacion: str):
    try:
        if password_nuevo != password_confirmacion:
            return None, "Las contraseñas nuevas no coinciden"

        # Validar credenciales creando un cliente temporal
        temp_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        auth_response = temp_client.auth.sign_in_with_password({
            "email":    email,
            "password": password_actual
        })

        if not auth_response.user:
            return None, "La contraseña actual es incorrecta"

        # Actualizar contraseña usando la sesión del cliente temporal
        temp_client.auth.update_user({"password": password_nuevo})

        return {"mensaje": "Contraseña actualizada correctamente"}, None

    except Exception as e:
        return None, f"Error inesperado: {str(e)}"
    
def crear_administrador(id_unphu: str, email: str, password: str, nombre: str):
    try:
        # Usamos el cliente global (Service Role) para crear el usuario en Auth
        auth_response = supabase.auth.admin.create_user({
            "email":         email,
            "password":      password,
            "email_confirm": True
        })

        if not auth_response.user:
            return None, "Error al crear el usuario en Auth"

        user_id = auth_response.user.id

        # Registrar en profiles
        supabase.table("profiles").insert({
            "id":       user_id,
            "id_unphu": id_unphu,
            "rol":      "administrador"
        }).execute()

        return {
            "mensaje":  f"Administrador '{nombre}' creado correctamente",
            "id_unphu": id_unphu,
            "email":    email,
            "rol":      "administrador"
        }, None

    except Exception as e:
        return None, f"Error inesperado: {str(e)}"