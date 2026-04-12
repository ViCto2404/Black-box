from app.database.supabase_client import supabase


def login(email: str, password: str):
    try:
        # Autenticar con Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not response.user:
            return None, "Credenciales incorrectas"

        user_id = response.user.id
        access_token = response.session.access_token

        # Obtener el perfil y rol del usuario
        perfil = supabase.table("profiles") \
            .select("rol, id_unphu") \
            .eq("id", user_id) \
            .single() \
            .execute()

        if not perfil.data:
            return None, "El usuario no tiene un perfil asignado en el sistema"

        rol     = perfil.data["rol"]
        id_unphu = str(perfil.data["id_unphu"]).strip()

        # Obtener el nombre y otros datos según el rol
        nombre = "Usuario"
        codigo_escuela = None

        if rol == "estudiante":
            data = supabase.table("estudiantes") \
                .select("nombre") \
                .eq("id_unphu", id_unphu) \
                .single() \
                .execute()
            if data.data:
                nombre = data.data["nombre"]
        elif rol == "director":
            # Búsqueda más robusta en directores
            data = supabase.table("directores") \
                .select("*") \
                .eq("id_unphu", id_unphu) \
                .execute()
            
            if data.data and len(data.data) > 0:
                director = data.data[0]
                nombre = director.get("nombre", "Director")
                codigo_escuela = director.get("codigo_escuela")
                print(f"DEBUG: Director encontrado: {nombre}, Escuela: {codigo_escuela}")
            else:
                print(f"DEBUG: No se encontró registro en 'directores' para ID: {id_unphu}")
        elif rol == "administrador":
            nombre = "Administrador"

        print(f"DEBUG LOGIN: Rol={rol}, Escuela={codigo_escuela}")

        return {
            "access_token": access_token,
            "token_type":   "bearer",
            "rol":          rol,
            "id_unphu":     id_unphu,
            "nombre":       nombre,
            "codigo_escuela": codigo_escuela
        }, None

    except Exception as e:
        return None, "Credenciales incorrectas"


def _get_nombre(rol: str, id_unphu: str) -> str:
    try:
        if rol == "estudiante":
            data = supabase.table("estudiantes") \
                .select("nombre") \
                .eq("id_unphu", id_unphu) \
                .single() \
                .execute()
        elif rol == "director":
            data = supabase.table("director") \
                .select("nombre") \
                .eq("id_unphu", id_unphu) \
                .single() \
                .execute()
        elif rol == "administrador":
            data = supabase.table("profiles") \
                .select("id_unphu") \
                .eq("id_unphu", id_unphu) \
                .single() \
                .execute()
            return "Administrador"
        else:
            return "Usuario"

        return data.data["nombre"] if data.data else "Usuario"
    except:
        return "Usuario"


def logout(token: str):
    try:
        supabase.auth.sign_out()
        return True, None
    except Exception as e:
        return False, str(e)
    
def cambiar_contrasena(email: str, password_actual: str, password_nuevo: str, password_confirmacion: str):
    try:
        # Verificar que las contraseñas nuevas coinciden
        if password_nuevo != password_confirmacion:
            return None, "Las contraseñas nuevas no coinciden"

        # Verificar longitud mínima
        if len(password_nuevo) < 6:
            return None, "La contraseña nueva debe tener al menos 6 caracteres"

        # Verificar que la contraseña nueva es diferente a la actual
        if password_actual == password_nuevo:
            return None, "La contraseña nueva debe ser diferente a la actual"

        # Verificar credenciales actuales e iniciar sesión
        auth_response = supabase.auth.sign_in_with_password({
            "email":    email,
            "password": password_actual
        })

        if not auth_response.user:
            return None, "La contraseña actual es incorrecta"

        # Usar el cliente con el token del usuario para actualizar
        from supabase import create_client
        from app.config import SUPABASE_URL, SUPABASE_KEY

        cliente_usuario = create_client(SUPABASE_URL, SUPABASE_KEY)
        cliente_usuario.auth.set_session(
            auth_response.session.access_token,
            auth_response.session.refresh_token
        )

        cliente_usuario.auth.update_user({"password": password_nuevo})

        return {"mensaje": "Contraseña actualizada correctamente"}, None

    except Exception as e:
        if "Invalid login credentials" in str(e):
            return None, "La contraseña actual es incorrecta"
        return None, f"Error inesperado: {str(e)}"
    
def crear_administrador(id_unphu: str, email: str, password: str, nombre: str):
    try:
        # Verificar que el id_unphu no esté en uso
        perfil = supabase.table("profiles") \
            .select("id_unphu") \
            .eq("id_unphu", id_unphu) \
            .execute()
        if perfil.data:
            return None, "El ID UNPHU ya está en uso"

        # Verificar que el correo no esté en uso en Auth
        usuarios = supabase.auth.admin.list_users()
        emails_existentes = [u.email for u in usuarios]
        if email in emails_existentes:
            return None, "El correo ya está en uso"

        # Verificar longitud mínima de contraseña
        if len(password) < 6:
            return None, "La contraseña debe tener al menos 6 caracteres"

        # Crear usuario en Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email":         email,
            "password":      password,
            "email_confirm": True
        })

        if not auth_response.user:
            return None, "Error al crear el usuario en Auth"

        user_id = auth_response.user.id

        # Registrar en profiles como administrador
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