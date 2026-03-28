import pandas as pd
from app.database.supabase_client import supabase

def get_feedback(es_anonimo: bool = None, codigo_carrera: str = None):
    data = supabase.table("feedback")\
            .select("id_feedback, id_estudiante, aspectos_evaluar, comentario, es_anonimo, fecha_envio")\
            .order("fecha_envio", desc=True)\
            .execute()
    
    if not data.data:
        return[]
    
    df = pd.DataFrame(data.data)

    estudiantes = supabase.table("estudiantes")\
                    .select("id_unphu, nombre, codigo_carrera")\
                    .execute()
    
    if estudiantes.data:
        df_est = pd.DataFrame(estudiantes.data)\
                .rename(columns={"id_unphu": "id_estudiante"})
        df = df.merge(df_est, on="id_estudiante", how="left")
    else:
        df["nombre"] = None
        df["codigo_carrera"] = None

    df["estudiante"] = df.apply(
        lambda row: "Anonimo" if row["es_anonimo"] else row.get("nombre"), axis=1
    )

    df["codigo_carrera"] = df.apply(
        lambda row: None if row["es_anonimo"] else row.get("codigo_carrera"), axis=1
    )

    if es_anonimo is not None:
        df = df[df["es_anonimo"] == es_anonimo]
    if codigo_carrera:
        df = df[df["codigo_carrera"] == codigo_carrera]

    df = df.drop(columns=["id_estudiante", "nombre"], errors="ignore")

    return df.to_dict("records")

def crear_feedback(payload: dict):
    try:
        if not payload.get("es_anonimo") and payload.get("id_estudiante"):
            estudiante = supabase.table("estudiantes")\
                        .select("id_unphu")\
                        .eq("id_unphu", payload["id_estudiante"])\
                        .execute()

            if not estudiante.data:
                return None, f"El estudiante {payload["id_estudiante"]} no existe"
            
        if payload.get("es_anonimo"):
            payload["id_estudiante"] = None
        
        data = supabase.table("feedback")\
                .insert(payload)\
                .execute()
        
        if not data.data:
            return None, "Error al registrar el feedback"
        
        return data.data[0], None
    
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"
    
def eliminar_feedback(id_feedback: int):
    try:
        data = supabase.table("feedback")\
                .delete()\
                .eq("id_feedback", id_feedback)\
                .execute()
        
        if not data.data:
            return False, "Feedback no encontrado"
        
        return True, None
    
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"
    
def get_resumen_feedback():
    data = supabase.table("feedback") \
        .select("aspectos_evaluar, es_anonimo") \
        .execute()

    if not data.data:
        return {}

    df = pd.DataFrame(data.data)
    print("Columnas recibidas:", df.columns.tolist())
    print("Primeras filas:", df.head())

    total = len(df)
    anonimos = int(df["es_anonimo"].sum())
    identificados = total - anonimos

    aspectos_serie = df["aspectos_evaluar"].dropna()
    todos_aspectos = []
    for val in aspectos_serie:
        todos_aspectos.extend([a.strip() for a in str(val).split(",")])

    df_aspectos = pd.Series(todos_aspectos).value_counts().reset_index()
    df_aspectos.columns = ["aspecto", "frecuencia"]

    return {
        "total_feedback":            total,
        "anonimos":                  anonimos,
        "identificados":             identificados,
        "aspectos_mas_mencionados":  df_aspectos.to_dict(orient="records")
    }