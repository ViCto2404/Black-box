import pandas as pd
from io import BytesIO
from app.database.supabase_client import supabase

def get_todos_estudiantes(codigo_carrera: str = None, estado: str = None):
    query = supabase.table("estudiantes") \
        .select("*, carreras(nombre)")
    
    if codigo_carrera:
        query = query.eq("codigo_carrera", codigo_carrera)
    if estado:
        query = query.eq("estado_activo", estado)

    data = query.execute()
    if not data.data:
        return []
    
    df = pd.DataFrame(data.data)
    df["nombre_carrera"] = df["carreras"].apply(lambda x: x["nombre"] if isinstance(x, dict) else None)
    df.drop(columns=["carreras"])

    return df.to_dict(orient="records")

def get_estudiante_por_id(id_unphu: str):
    data = supabase.table("estudiantes")\
        .select("*, carreras(nombre)")\
        .eq("id_unphu", id_unphu)\
        .single()\
        .execute()
    
    if not data.data:
        return None
    
    estudiante = data.data
    if isinstance(estudiante.get("carreras"), dict):
        estudiante["nombre_carrera"] = estudiante["carreras"]["nombre"]
    estudiante.pop("carreras", None)

    return estudiante

def crear_estudiante(payload: dict):
    try:
        existente = supabase.table("estudiantes") \
            .select("id_unphu") \
            .eq("id_unphu", payload["id_unphu"]) \
            .execute()
        if existente.data:
            return None, "El ID UNPHU ya existe en el sistema"

        if not payload.get("correo_institucional"):
            return None, "El correo institucional es obligatorio para crear el usuario"

        # Crear usuario en Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email":    payload["correo_institucional"],
            "password": payload["id_unphu"],  # contraseña temporal = id_unphu
            "email_confirm": True
        })

        if not auth_response.user:
            return None, "Error al crear el usuario de autenticación"

        user_id = auth_response.user.id

        # Insertar en la tabla estudiantes
        data = supabase.table("estudiantes").insert(payload).execute()
        if not data.data:
            return None, "Error al crear el estudiante"

        # Registrar en profiles
        supabase.table("profiles").insert({
            "id":       user_id,
            "id_unphu": payload["id_unphu"],
            "rol":      "estudiante"
        }).execute()

        return {
            **data.data[0],
            "mensaje": f"Usuario creado. Contraseña temporal: {payload['id_unphu']}"
        }, None

    except Exception as e:
        return None, f"Error inesperado: {str(e)}"

def actualizar_estado(id_unphu: str, estado: str):
    if estado not in ("Activo", "Inactivo"):
        return None, "Estado invalido, use 'Activo' o 'Inactivo'"
    
    data = supabase.table("estudiantes")\
        .update({"estado_activo": estado})\
        .eq("id_unphu", id_unphu)\
        .execute()
    
    if not data.data:
        return None, "Estudiante no encontrado"
    
    return data.data[0], None

def actualizar_estudiante(id_unphu: str, payload: dict):
    payload_limpio = {k:v for k, v in payload.items() if v is not None}

    if not payload_limpio:
        return None, "No hay campos para actualizar"
    
    data = supabase.table("estudiantes")\
    .update(payload_limpio)\
    .eq("id_unphu", id_unphu)\
    .execute()

    if not data.data:
        return False, "Estudiante no encontrado"
    
    return data.data[0], None

def eliminar_estudiante(id_unphu: str):
    data = supabase.table("estudiantes")\
    .delete()\
    .eq("id_unphu", id_unphu)\
    .execute()

    if not data.data:
        return False, "Estudiante no encontrado"
    
    return True, None

def carga_masiva_estudiantes(registros: list):
    if not registros:
        return {"insertados": 0, "errores": []}

    errores = []
    insertados = 0

    for r in registros:
        resultado, error = crear_estudiante(r)
        if error:
            errores.append(f"Error en {r['id_unphu']}: {error}")
        else:
            insertados += 1

    return {"insertados": insertados, "errores": errores}

def generar_plantilla_estudiante():
    columnas = ["id_unphu", "nombre", "codigo_carrera", "estado_activo", "correo_institucional", "periodo_inscripcion"]
    df = pd.DataFrame(columns=columnas)

    ejemplo = {
        "id_unphu": "20-0001",
        "nombre": "Juan Perez",
        "codigo_carrera": "INF",
        "estado_activo": "Activo",
        "correo_institucional": "j.perez@unphu.edu.do",
        "periodo_inscripcion": "01-2025"
    }
    df.loc[0] = ejemplo

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Plantilla Estudiantes')

    return output.getvalue()
