import pandas as pd
from app.database.supabase_client import supabase

def _ejecutar_query(query):
    resultado = query.execute()
    if hasattr(resultado, "data"):
        return resultado.data
    return resultado

def get_periodos():
    """
    Obtiene todos los periodos académicos únicos de la tabla de calificaciones.
    """
    try:
        query = supabase.table("calificacion").select("periodo_academico").execute()
        if not query.data:
            return []
        
        # Extraer valores únicos
        periodos = sorted(list(set(item["periodo_academico"] for item in query.data)), reverse=True)
        return periodos
    except Exception as e:
        print(f"Error obteniendo periodos: {str(e)}")
        return []

def get_rendimiento_por_materia(periodo:str, codigo_escuela: str= None, codigo_carrera: str = None):
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
    df["nombre_materia"] = df["materia"].apply(lambda x: x["nombre"] if isinstance(x, dict) else None)
    df["codigo_carrera"] = df["materia"].apply(lambda x: x["codigo_carrera"] if isinstance(x, dict) else None)
    df["estado_materia"] = df["materia"].apply(lambda x: x["estado"] if isinstance(x, dict) else None)
    
    df = df.dropna(subset=["nombre_materia"])

    if df.empty:
        return []
    
    resumen = df.groupby(["codigo_materia", "nombre_materia", "codigo_carrera", "estado_materia"]).agg(
        total_estudiantes = ("nota", "count"),
        promedio=("nota", "mean"),
        aprobados=("nota", lambda x: (x>=70).sum()),
        reprobados=("nota", lambda x: (x<70).sum())
    ).reset_index()

    resumen["porcentaje_aprobacion"] = round(resumen["aprobados"] / resumen["total_estudiantes"] * 100 , 2)
    resumen["porcentaje_reprobacion"] = round(resumen["reprobados"] / resumen["total_estudiantes"] * 100 , 2)
    resumen["promedio"] = resumen["promedio"].round(2)
    resumen["periodo_academico"] = periodo

    return resumen.to_dict(orient="records")

def get_materias_criticas(periodo: str, codigo_escuela: str= None, codigo_carrera: str = None, umbral: float = 30.0):
    rendimiento = get_rendimiento_por_materia(periodo, codigo_escuela, codigo_carrera)
    if not rendimiento:
        return []
    
    df = pd.DataFrame(rendimiento)
    df_criticas = df[df["porcentaje_reprobacion"] > umbral].copy()
    
    if df_criticas.empty:
        return []

    df_criticas["umbral_reprobacion"] = umbral
    columnas_solicitadas = ["codigo_materia", "nombre_materia", "codigo_carrera", "total_estudiantes", "promedio", "porcentaje_reprobacion", "umbral_reprobacion"]
    
    return df_criticas[columnas_solicitadas].sort_values("porcentaje_reprobacion", ascending=False).to_dict(orient="records")

def get_resumen_periodo(periodo: str, escuela: str = None, codigo_carrera: str = None, codigo_materia: str = None):
    print(f"DEBUG: get_resumen_periodo - Periodo: {periodo}, Escuela: {escuela}, Carrera: {codigo_carrera}, Materia: {codigo_materia}")
    
    # Consulta dinámica
    select_fields = "nota, id_seccion, id_estudiante"
    
    # Si hay filtros externos que requieren join
    if escuela or codigo_carrera:
        select_fields += ", materia!inner(codigo_carrera, carreras!inner(codigo_escuela))"
        
    query = supabase.table("calificacion").select(select_fields).eq("periodo_academico", periodo)
    
    if escuela:
        query = query.eq("materia.carreras.codigo_escuela", escuela)
    
    if codigo_carrera:
        query = query.eq("materia.codigo_carrera", codigo_carrera)
        
    if codigo_materia:
        query = query.eq("codigo_materia", codigo_materia)

    try:
        data = _ejecutar_query(query)
    except Exception as e:
        print(f"ERROR en query de resumen: {str(e)}")
        return {
            "total_secciones_analizadas": 0,
            "secciones_criticas": 0,
            "promedio_general": 0.0,
            "indice_aprobacion": 0.0,
            "total_estudiantes": 0,
            "error": str(e),
            "debug_params": {"periodo": periodo, "escuela": escuela, "codigo_carrera": codigo_carrera}
        }

    if not data:
        return {
            "total_secciones_analizadas": 0,
            "secciones_criticas": 0,
            "promedio_general": 0.0,
            "indice_aprobacion": 0.0,
            "total_estudiantes": 0,
            "debug_msg": f"No data found for period: {periodo}, escuela: {escuela}"
        }
    
    df = pd.DataFrame(data)
    df["nota"] = pd.to_numeric(df["nota"], errors='coerce')
    df = df.dropna(subset=["nota"])

    if df.empty:
        return {
            "total_secciones_analizadas": 0,
            "secciones_criticas": 0,
            "promedio_general": 0.0,
            "indice_aprobacion": 0.0,
            "total_estudiantes": 0,
            "debug_msg": "Data found but 'nota' column is empty or invalid"
        }

    total_secciones = int(df["id_seccion"].nunique())
    total_estudiantes = int(df["id_estudiante"].nunique())
    
    resumen_secciones = df.groupby("id_seccion").agg(
        total_estudiantes_seccion=("nota", "count"),
        reprobados=("nota", lambda x: (x < 70).sum())
    )
    resumen_secciones["porcentaje_reprobacion"] = (resumen_secciones["reprobados"] / resumen_secciones["total_estudiantes_seccion"]) * 100
    secciones_criticas = int((resumen_secciones["porcentaje_reprobacion"] > 30).sum())

    promedio_general = round(float(df["nota"].mean()), 2)
    indice_aprobacion = round(float((df["nota"] >= 70).sum() / len(df) * 100), 2)

    return {
        "total_secciones_analizadas": total_secciones,
        "secciones_criticas": secciones_criticas,
        "promedio_general": promedio_general,
        "indice_aprobacion": indice_aprobacion,
        "total_estudiantes": total_estudiantes
    }

def get_masa_estudiantil(codigo_carrera: str = None, escuela: str = None):
    # ESTRATEGIA: Si hay escuela, primero buscamos qué carreras pertenecen a esa escuela
    codigos_carreras_permitidos = []
    
    if escuela:
        try:
            res_carreras = supabase.table("carreras").select("codigo").eq("codigo_escuela", escuela).execute()
            if res_carreras.data:
                codigos_carreras_permitidos = [c["codigo"] for c in res_carreras.data]
                print(f"DEBUG MASA: Carreras permitidas para escuela {escuela}: {codigos_carreras_permitidos}")
            else:
                print(f"DEBUG MASA: No se encontraron carreras para la escuela {escuela}")
                return []
        except Exception as e:
            print(f"ERROR obteniendo carreras para escuela: {str(e)}")
            return []

    # Ahora consultamos los estudiantes
    query = supabase.table("estudiantes").select("id_unphu, estado_activo, codigo_carrera, carreras(nombre)")
    
    if codigo_carrera:
        query = query.eq("codigo_carrera", codigo_carrera)
    
    # Filtro manual por la lista de carreras de la escuela
    if escuela and codigos_carreras_permitidos:
        query = query.in_("codigo_carrera", codigos_carreras_permitidos)

    try:
        data = _ejecutar_query(query)
        print(f"DEBUG MASA: Estudiantes encontrados tras filtro: {len(data) if data else 0}")
    except Exception as e:
        print(f"ERROR en get_masa_estudiantil: {str(e)}")
        return []

    if not data:
        return []
    
    df = pd.DataFrame(data)
    df["nombre_carrera"] = df["carreras"].apply(lambda x: x["nombre"] if isinstance(x, dict) else "N/A")

    # Agrupar y resumir
    resumen = df.groupby(["codigo_carrera", "nombre_carrera"]).agg(
        total_activos = ("estado_activo", lambda x: int((x=="Activo").sum())),
        total_inactivos=("estado_activo", lambda x: int((x == "Inactivo").sum())),
        total_general=("id_unphu", "count" )
    ).reset_index()

    return resumen.to_dict(orient="records")

def get_detalle_materia_secciones(codigo_materia: str, periodo: str):
    """
    Obtiene el detalle de rendimiento de una materia específica, desglosado por todas sus secciones registradas.
    Toma como base la tabla 'seccion' para asegurar que aparezcan todas las filas (secciones) existentes.
    """
    try:
        # 1. Obtener todas las secciones registradas para esa materia y periodo
        # Traemos también el nombre de la materia a través de la relación
        query_secciones = supabase.table("seccion") \
            .select("id, codigo_seccion, materia!inner(nombre), profesor!inner(nombre)") \
            .eq("materia", codigo_materia) \
            .eq("periodo", periodo)
        
        data_secciones = _ejecutar_query(query_secciones)
        if not data_secciones:
            return []
        
        # ... (resto de la lógica de notas igual)
        
        # 2. Obtener TODAS las calificaciones para esta materia y periodo
        query_notas = supabase.table("calificacion") \
            .select("nota, id_seccion, id_estudiante") \
            .eq("codigo_materia", codigo_materia) \
            .eq("periodo_academico", periodo)
        
        data_notas = _ejecutar_query(query_notas)
        df_notas = pd.DataFrame(data_notas) if data_notas else pd.DataFrame(columns=["nota", "id_seccion", "id_estudiante"])

        # Procesar los datos de las secciones
        resultados = []
        for sec in data_secciones:
            sid = sec["id"]
            cod_visual = sec["codigo_seccion"]
            nombre_mat = sec["materia"]["nombre"] if isinstance(sec.get("materia"), dict) else "N/A"
            nombre_prof = sec["profesor"]["nombre"] if isinstance(sec.get("profesor"), dict) else "N/A"
            
            # Filtrar notas para esta sección específica
            notas_seccion = df_notas[df_notas["id_seccion"] == sid]
            
            total_est = len(notas_seccion)
            if total_est > 0:
                promedio = round(notas_seccion["nota"].mean(), 2)
                aprobados = (notas_seccion["nota"] >= 70).sum()
                porcentaje_aprobacion = round((aprobados / total_est) * 100, 2)
            else:
                promedio = 0.0
                aprobados = 0
                porcentaje_aprobacion = 0.0
            
            estado = "Crítico" if (total_est > 0 and porcentaje_aprobacion < 70) else "Normal"
            
            resultados.append({
                "seccion_id_pk": sid,
                "id_seccion_display": cod_visual,
                "nombre_materia": nombre_mat,
                "nombre_profesor": nombre_prof,
                "total_estudiantes": total_est,
                "promedio": promedio,
                "porcentaje_aprobacion": porcentaje_aprobacion,
                "estado": estado
            })
            
        return resultados
    except Exception as e:
        print(f"Error en get_detalle_materia_secciones: {str(e)}")
        return []

def get_detalle_feedback(codigo_carrera: str = None):
    query = supabase.table("feedback").select('fecha_envio, aspectos_evaluar, es_anonimo, comentario, id_estudiante, "queja/sugerencia"').order("fecha_envio", desc=True)
    data = _ejecutar_query(query)
    if not data:
        return []
    
    df = pd.DataFrame(data)
    est_query = supabase.table("estudiantes").select("id_unphu, codigo_carrera")
    est_data = _ejecutar_query(est_query)
    
    if est_data:
        df_est = pd.DataFrame(est_data).rename(columns={"id_unphu": "id_estudiante"})
        df = df.merge(df_est, on="id_estudiante", how="left")
        
    df["codigo_carrera"] = df.apply(lambda row: "N/A" if row["es_anonimo"] else row.get("codigo_carrera", "N/A"), axis=1)
    if codigo_carrera:
        df = df[df["codigo_carrera"] == codigo_carrera]
        
    df["es_anonimo_str"] = df["es_anonimo"].apply(lambda x: "Sí" if x else "No")
    return df[["fecha_envio", "codigo_carrera", "aspectos_evaluar", "es_anonimo_str", "comentario", "queja/sugerencia", "id_estudiante"]].to_dict(orient="records")
