import pandas as pd
from app.database.supabase_client import supabase

def _ejecutar_query(query):
    resultado = query.execute()
    if hasattr(resultado, "data"):
        return resultado.data
    return resultado

def get_rendimiento_por_materia(periodo:str, codigo_escuela: str= None, codigo_carrera: str = None):
    query = supabase.table("calificacion") \
        .select("nota, codigo_materia, id_estudiante, materia!inner(" \
        "codigo, " \
        "nombre, " \
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
    df["nombre_materia"] = df["materia"].apply(lambda x: x["nombre"] if isinstance(x, dict) else None)
    df["codigo_carrera"] = df["materia"].apply(lambda x: x["codigo_carrera"] if isinstance(x, dict) else None)
    df.dropna(subset=["nombre_materia"])

    if codigo_carrera:
        df = df[df["codigo_carrera"] == codigo_carrera]

    if df.empty:
        return []
    
    resumen = df.groupby(["codigo_materia", "nombre_materia", "codigo_carrera"]).agg(
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
    criticas = df[df["porcentaje_reprobacion"] > umbral] \
            .sort_values("porcentaje_reprobacion", ascending=False)
    
    return criticas.to_dict(orient="records")

def get_resumen_periodo(periodo:str, escuela: str = None):
    query = supabase.table("calificacion") \
        .select("nota, codigo_materia, id_estudiante, materia!inner(codigo_carrera, carreras!inner(codigo_escuela))") \
        .eq("periodo_academico", periodo)
    
    if escuela:
        query = query.eq("materia.carreras.codigo_escuela", escuela)

    data = _ejecutar_query(query)

    if not data:
        return{"Estudiantes vacio": True}
    
    df = pd.DataFrame(data)

    total_estudiantes = int(df["id_estudiante"].nunique())
    total_materias = int(df["codigo_materia"].nunique())
    indice_aprobacion = round(float((df["nota"] >=70).sum()/len(df)*100), 2)
    criticas = get_materias_criticas(periodo)

    return {
        "total_estudiantes_analizados": total_estudiantes,
        "total materias": total_materias,
        "indice_aprobacion_global": indice_aprobacion,
        "cantidad_materias_criticas": len(criticas)
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