import pandas as pd
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
    existente = supabase.table("estudiantes")\
    .select("id_unphu")\
    .eq("id_unphu", payload["id_unphu"])\
    .execute()

    if existente.data:
        return None, "El ID UNPHU ya existe en el sistema"
    
    data = supabase.table("estudiantes")\
    .insert(payload)\
    .execute()

    if not data.data:
        return None, "Error al crear el estudiante"
    
    return data.data[0], None

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