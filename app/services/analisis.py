import pandas as pd
from app.database.supabase_client import supabase

def _ejecutar_query(query):
    resultado = query.execute()
    if hasattr(resultado, "data"):
        return resultado.data
    return resultado

def get_rendimiento_por_materia(periodo:str, codigo_escuela: str= None, codigo_carrera: str = None):
    # Agregamos 'estado' al select de materia
    query = supabase.table("calificacion") \
        .select("nota, codigo_materia, id_estudiante, materia!inner(" \
        "codigo, " \
        "nombre, " \
        "estado, " \
        "codigo_carrera, " \
        "carreras!inner(codigo_escuela))") \
        .eq("periodo_academico", periodo)
    
    if codigo_escuela:
        query = query.eq("materia.carreras.codigo_escuela", codigo_escuela)
    
    if codigo_carrera:
        query = query.eq("materia.codigo_carrera", codigo_carrera)

    data = _ejecutar_query(query)

    if not data:
        return []
    
    df = pd.DataFrame(data)
    # Extraemos campos de la relación materia
    df["nombre_materia"] = df["materia"].apply(lambda x: x["nombre"] if isinstance(x, dict) else None)
    df["codigo_carrera"] = df["materia"].apply(lambda x: x["codigo_carrera"] if isinstance(x, dict) else None)
    df["estado_materia"] = df["materia"].apply(lambda x: x["estado"] if isinstance(x, dict) else None)
    
    df.dropna(subset=["nombre_materia"])

    if codigo_carrera:
        df = df[df["codigo_carrera"] == codigo_carrera]

    if df.empty:
        return []
    
    # Agrupamos incluyendo el estado
    resumen = df.groupby(["codigo_materia", "nombre_materia", "codigo_carrera", "estado_materia"]).agg(
        total_estudiantes = ("nota", "count"),
        promedio=("nota", "mean"),
        aprobados=("nota", lambda x: (x>=70).sum()),
        reprobados=("nota", lambda x: (x<70).sum())
    ).reset_index()

    resumen["porcentaje_aprobacion"] = round(
        resumen["aprobados"] / resumen["total_estudiantes"] * 100 , 2
    )

    resumen["porcentaje_reprobacion"] = round(
        resumen["reprobados"] / resumen["total_estudiantes"] * 100 , 2
    )

    resumen["promedio"] = resumen["promedio"].round(2)
    resumen["periodo_academico"] = periodo

    resumen = resumen.drop(columns=["aprobados", "reprobados"])

    return resumen.to_dict(orient="records")

def get_materias_criticas(periodo: str, codigo_escuela: str= None, codigo_carrera: str = None, umbral: float = 30.0):
    rendimiento = get_rendimiento_por_materia(periodo, codigo_escuela, codigo_carrera)

    if not rendimiento:
        return []
    
    df = pd.DataFrame(rendimiento)
    # Filtramos por el umbral
    df_criticas = df[df["porcentaje_reprobacion"] > umbral].copy()
    
    if df_criticas.empty:
        return []

    # Agregamos el umbral utilizado al reporte
    df_criticas["umbral_reprobacion"] = umbral
    
    # Seleccionamos los campos solicitados, incluyendo el promedio
    columnas_solicitadas = [
        "codigo_materia", 
        "nombre_materia", 
        "codigo_carrera", 
        "total_estudiantes", 
        "promedio",
        "porcentaje_reprobacion", 
        "umbral_reprobacion"
    ]
    
    # Aseguramos que solo devolvemos lo que se pidió
    df_criticas = df_criticas[columnas_solicitadas].sort_values("porcentaje_reprobacion", ascending=False)
    
    return df_criticas.to_dict(orient="records")

def get_resumen_periodo(periodo:str, escuela: str = None):
    query = supabase.table("calificacion") \
        .select("nota, codigo_materia, id_estudiante, id_seccion, materia!inner(codigo_carrera, carreras!inner(codigo_escuela))") \
        .eq("periodo_academico", periodo)
    
    if escuela:
        query = query.eq("materia.carreras.codigo_escuela", escuela)

    data = _ejecutar_query(query)

    if not data:
        return {
            "total_secciones_analizadas": 0,
            "secciones_criticas": 0,
            "promedio_general": 0,
            "indice_aprobacion": 0
        }
    
    df = pd.DataFrame(data)

    total_secciones = int(df["id_seccion"].nunique())

    resumen_secciones = df.groupby("id_seccion").agg(
        total_estudiantes=("nota", "count"),
        reprobados=("nota", lambda x: (x < 70).sum())
    )
    resumen_secciones["porcentaje_reprobacion"] = (resumen_secciones["reprobados"] / resumen_secciones["total_estudiantes"]) * 100
    secciones_criticas = int((resumen_secciones["porcentaje_reprobacion"] > 30).sum())

    promedio_general = round(float(df["nota"].mean()), 2)
    indice_aprobacion = round(float((df["nota"] >= 70).sum() / len(df) * 100), 2)

    return {
        "total_secciones_analizadas": total_secciones,
        "secciones_criticas": secciones_criticas,
        "promedio_general": promedio_general,
        "indice_aprobacion": indice_aprobacion
    }

def get_masa_estudiantil(codigo_carrera: str = None):
    query = supabase.table("estudiantes") \
        .select("id_unphu, estado_activo, codigo_carrera, carreras(nombre)")
    
    if codigo_carrera:
        query = query.eq("codigo_carrera", codigo_carrera)

    data = _ejecutar_query(query)

    if not data:
        return []
    
    df = pd.DataFrame(data)
    df["nombre_carrera"] = df["carreras"].apply(lambda x: x["nombre"] if isinstance(x, dict) else None)

    resumen = df.groupby(["codigo_carrera", "nombre_carrera"]).agg(
        total_activos = ("estado_activo", lambda x: int((x=="Activo").sum())),
        total_inactivos=("estado_activo", lambda x: int((x == "Inactivo").sum())),
        total_general=("id_unphu", "count" )
    ).reset_index()

    resumen["total_general"] = resumen["total_general"].astype(int)

    return resumen.to_dict(orient="records")

def get_detalle_feedback(codigo_carrera: str = None):
    query = supabase.table("feedback") \
        .select("fecha_envio, aspectos_evaluar, es_anonimo, comentario, id_estudiante") \
        .order("fecha_envio", desc=True)
    
    data = _ejecutar_query(query)
    if not data:
        return []
    
    df = pd.DataFrame(data)
    
    # Traer info de estudiantes para la carrera
    est_query = supabase.table("estudiantes").select("id_unphu, codigo_carrera")
    est_data = _ejecutar_query(est_query)
    
    if est_data:
        df_est = pd.DataFrame(est_data).rename(columns={"id_unphu": "id_estudiante"})
        df = df.merge(df_est, on="id_estudiante", how="left")
    else:
        df["codigo_carrera"] = None
        
    # Si es anónimo, ocultamos la carrera (según lógica previa en feedback.py)
    df["codigo_carrera"] = df.apply(
        lambda row: "N/A" if row["es_anonimo"] else row.get("codigo_carrera", "N/A"), axis=1
    )
    
    if codigo_carrera:
        df = df[df["codigo_carrera"] == codigo_carrera]
        
    df["es_anonimo_str"] = df["es_anonimo"].apply(lambda x: "Sí" if x else "No")
    
    # Seleccionar columnas finales
    df = df[["fecha_envio", "codigo_carrera", "aspectos_evaluar", "es_anonimo_str", "comentario"]]
    
    return df.to_dict(orient="records")
