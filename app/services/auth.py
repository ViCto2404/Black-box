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
        id_unphu = perfil.data["id_unphu"]

        # Obtener el nombre según el rol
        nombre = _get_nombre(rol, id_unphu)

        return {
            "access_token": access_token,
            "token_type":   "bearer",
            "rol":          rol,
            "id_unphu":     id_unphu,
            "nombre":       nombre
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