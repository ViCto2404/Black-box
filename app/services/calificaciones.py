import pandas as pd
from app.database.supabase_client import supabase

def get_calificaciones(periodo: str = None, id_estudiante: str = None, codigo_materia: str = None):
    query = supabase.table("calificacion") \
        .select("*")

    if periodo:
        query = query.eq("periodo_academico", periodo)
    if id_estudiante:
        query = query.eq("id_estudiante", id_estudiante)
    if codigo_materia:
        query = query.eq("codigo_materia", codigo_materia)

    data = query.execute()
    if not data.data:
        return []

    df = pd.DataFrame(data.data)

    # Traer nombres de materias por separado y hacer merge
    materias = supabase.table("materia") \
        .select("codigo, nombre") \
        .execute()

    if materias.data:
        df_materias = pd.DataFrame(materias.data) \
            .rename(columns={"codigo": "codigo_materia", "nombre": "nombre_materia"})
        df = df.merge(df_materias, on="codigo_materia", how="left")

    return df.to_dict(orient="records")

def crear_calificacion(payload: dict):
    existente = supabase.table("calificacion")\
                .select("id")\
                .eq("id_estudiante", payload["id_estudiante"])\
                .eq("codigo_materia", payload["codigo_materia"])\
                .eq("periodo_academico", payload["periodo_academico"])\
                .execute()
    
    if existente.data:
        return None, "Ya existe"
    
    data = supabase.table("calificacion")\
            .insert(payload)\
            .execute()
    
    if not data.data:
        return None, "Error al crear la calificacion"
    
    return data.data[0], None

def actualizar_calificacion(id: int, nota: float):
    if not 0 <= nota <= 100:
        return None, "La nota debe estar entre 0 y 100"
    
    data = supabase.table("calificacion")\
            .update({"nota": nota})\
            .eq("id", id)\
            .execute()
    
    if not data.data:
        return None, "Calificacion no encontrada"
    
    return data.data[0], None

def eliminar_calificacion(id: int):
    data = supabase.table("calificacion")\
            .delete()\
            .eq("id", id)\
            .execute()
    
    if not data.data:
        return False, "Calificacion no encontrada"
    
    return True, None

def carga_masiva(registros: list):
    if not registros:
        return {"insertados": 0, "errores": []}
    
    errores = []
    insertados = 0

    for r in registros:
        existente = supabase.table("calificacion")\
                    .select("id")\
                    .eq("id_estudiante", r["id_estudiante"])\
                    .eq("codigo_materia", r["codigo_materia"])\
                    .eq("periodo_academico", r["periodo_academico"])\
                    .execute()
        
        if existente.data:
            errores.append(f"Duplicado: {r["id_estudiante"]} - {r["codigo_materia"]} - {r["periodo_academico"]}")
            continue

        resultado = supabase.table("calificacion").insert(r).execute()
        if resultado.data:
            insertados +=1
        else:
            errores.append(f"Error al insertar: {r['id_estudiante']} - {r['codigo_materia']}")

    return {"insertados": insertados, "errores": errores}