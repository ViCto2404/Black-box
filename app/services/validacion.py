import pandas as pd
from io import BytesIO

COLUMNAS_CALIFICACIONES = {"id_estudiante", "codigo_materia", "id_seccion", "nota", "periodo_academico"}
COLUMNAS_SECCIONES = {"codigo_seccion", "materia", "profesor", "periodo", "aula", "cupo_max", "horario", "estado"}
COLUMNAS_ESTUDIANTES = {"id_unphu", "nombre", "codigo_carrera", "estado_activo", "correo_institucional"}

def leer_archivo(contenido: bytes, nombre_archivo: str) -> pd.DataFrame:
    if nombre_archivo.endswith(".csv"):
        df = pd.read_csv(BytesIO(contenido))
    elif nombre_archivo.endswith((".xlsx", ".xls")):
        df = pd.read_excel(BytesIO(contenido))
    else: 
        raise ValueError("Formato no soportado. Use CSV o Excel")
    return df

def validar_columnas(df: pd.DataFrame, requeridas: set):
    columnas_archivo = set(df.columns.str.strip().str.lower())
    faltantes = requeridas - columnas_archivo
    if faltantes:
        raise ValueError(f"Columnas faltantes en el archivo: {faltantes}")

def validar_notas(df: pd.DataFrame):
    df.columns = df.columns.str.strip().str.lower()
    errores = []

    for i, row in df.iterrows():
        fila = i+2

        # Validar id_estudiante
        if pd.isna(row.get("id_estudiante")) or str(row.get("id_estudiante")).strip() == "":
            errores.append(f"Fila {fila}: id_estudiante vacio")

        # Validar codigo_materia
        if pd.isna(row.get("codigo_materia")) or str(row.get("codigo_materia")).strip() == "":
            errores.append(f"Fila {fila}: codigo_materia vacio")

        # Validar id_seccion
        if pd.isna(row.get("id_seccion")):
            errores.append(f"Fila {fila}: id_seccion vacio")
        else:
            try:
                int(row["id_seccion"])
            except ValueError:
                errores.append(f"Fila {fila}: id_seccion '{row['id_seccion']}' no es un número entero")

        # Validar periodo_academico
        if pd.isna(row.get("periodo_academico")) or str(row.get("periodo_academico")).strip() == "":
            errores.append(f"Fila {fila}: periodo_academico vacio")

        # Validar nota
        if pd.isna(row.get("nota")):
            errores.append(f"Fila {fila}: nota vacía")
        else:
            try:
                nota = float(row["nota"])
                if not 0 <= nota <= 100:
                    errores.append(f"Fila {fila}: nota {nota} fuera del rango 0-100")
            except ValueError:
                errores.append(f"Fila {fila}: nota '{row['nota']}' no es un numero")
        
    return errores

def validar_datos_secciones(df: pd.DataFrame):
    df.columns = df.columns.str.strip().str.lower()
    errores = []

    for i, row in df.iterrows():
        fila = i+2

        if pd.isna(row.get("codigo_seccion")) or str(row.get("codigo_seccion")).strip() == "":
            errores.append(f"Fila {fila}: codigo_seccion vacio")

        if pd.isna(row.get("materia")) or str(row.get("materia")).strip() == "":
            errores.append(f"Fila {fila}: materia vacio")

        if pd.isna(row.get("periodo")) or str(row.get("periodo")).strip() == "":
            errores.append(f"Fila {fila}: periodo vacio")

        if pd.isna(row.get("cupo_max")):
            errores.append(f"Fila {fila}: cupo_max vacio")
        else:
            try:
                int(row["cupo_max"])
            except ValueError:
                errores.append(f"Fila {fila}: cupo_max '{row['cupo_max']}' no es un número entero")

    return errores

def validar_datos_estudiantes(df: pd.DataFrame):
    df.columns = df.columns.str.strip().str.lower()
    errores = []

    for i, row in df.iterrows():
        fila = i+2

        if pd.isna(row.get("id_unphu")) or str(row.get("id_unphu")).strip() == "":
            errores.append(f"Fila {fila}: id_unphu vacio")

        if pd.isna(row.get("nombre")) or str(row.get("nombre")).strip() == "":
            errores.append(f"Fila {fila}: nombre vacio")

        if pd.isna(row.get("codigo_carrera")) or str(row.get("codigo_carrera")).strip() == "":
            errores.append(f"Fila {fila}: codigo_carrera vacio")

        if pd.isna(row.get("correo_institucional")) or str(row.get("correo_institucional")).strip() == "":
            errores.append(f"Fila {fila}: correo_institucional vacio")
        elif "@" not in str(row.get("correo_institucional")):
            errores.append(f"Fila {fila}: correo_institucional '{row['correo_institucional']}' no es valido")

    return errores

def preparar_registros_calificaciones(df: pd.DataFrame) -> list:
    df.columns = df.columns.str.strip().str.lower()
    
    registros = []
    for _, row in df.iterrows():
        if pd.isna(row.get("id_estudiante")) or pd.isna(row.get("codigo_materia")) or pd.isna(row.get("id_seccion")):
            continue

        registros.append({
            "id_estudiante": str(row["id_estudiante"]).strip(),
            "codigo_materia": str(row["codigo_materia"]).strip(),
            "id_seccion": int(row["id_seccion"]),
            "nota": round(float(row["nota"]), 2),
            "periodo_academico": str(row["periodo_academico"]).strip()
        })

    return registros

def preparar_registros_secciones(df: pd.DataFrame) -> list:
    df.columns = df.columns.str.strip().str.lower()
    
    registros = []
    for _, row in df.iterrows():
        if pd.isna(row.get("codigo_seccion")) or pd.isna(row.get("materia")):
            continue

        registros.append({
            "codigo_seccion": str(row["codigo_seccion"]).strip(),
            "materia": str(row["materia"]).strip(),
            "profesor": str(row["profesor"]).strip() if not pd.isna(row.get("profesor")) else None,
            "periodo": str(row["periodo"]).strip(),
            "aula": str(row["aula"]).strip() if not pd.isna(row.get("aula")) else None,
            "cupo_max": int(row["cupo_max"]),
            "horario": str(row["horario"]).strip() if not pd.isna(row.get("horario")) else None,
            "estado": str(row["estado"]).strip() if not pd.isna(row.get("estado")) else "Activa"
        })

    return registros

def preparar_registros_estudiantes(df: pd.DataFrame) -> list:
    df.columns = df.columns.str.strip().str.lower()
    
    registros = []
    for _, row in df.iterrows():
        if pd.isna(row.get("id_unphu")) or pd.isna(row.get("nombre")):
            continue

        registros.append({
            "id_unphu": str(row["id_unphu"]).strip(),
            "nombre": str(row["nombre"]).strip(),
            "codigo_carrera": str(row["codigo_carrera"]).strip(),
            "estado_activo": str(row["estado_activo"]).strip() if not pd.isna(row.get("estado_activo")) else "Activa",
            "correo_institucional": str(row["correo_institucional"]).strip()
        })

    return registros

def validar_existencia_en_bd_calificaciones(registros: list):
    from app.database.supabase_client import supabase

    errores = []

    estudiantes = supabase.table("estudiantes")\
                .select("id_unphu")\
                .execute()
    materias = supabase.table("materia")\
                .select("codigo")\
                .execute()
    
    ids_estudiantes = {e["id_unphu"] for e in estudiantes.data}
    codigos_materias = {m["codigo"] for m in materias.data}

    for i, r in enumerate(registros):
        fila = i+2

        if r["id_estudiante"] not in ids_estudiantes:
            errores.append(f"Fila {fila}: el estudiante '{r['id_estudiante']}' no existe en el sistema")

        if r["codigo_materia"] not in codigos_materias:
            errores.append(f"Fila {fila}: la materia '{r['codigo_materia']}' no existe en el sistema")

    return errores

def validar_existencia_en_bd_secciones(registros: list):
    from app.database.supabase_client import supabase

    errores = []

    materias = supabase.table("materia")\
                .select("codigo")\
                .execute()
    profesores = supabase.table("profesor")\
                .select("id_profesor")\
                .execute()
    
    codigos_materias = {m["codigo"] for m in materias.data}
    ids_profesores = {p["id_profesor"] for p in profesores.data}

    for i, r in enumerate(registros):
        fila = i+2

        if r["materia"] not in codigos_materias:
            errores.append(f"Fila {fila}: la materia '{r['materia']}' no existe en el sistema")

        if r["profesor"] and r["profesor"] not in ids_profesores:
            errores.append(f"Fila {fila}: el profesor '{r['profesor']}' no existe en el sistema")

    return errores

def validar_existencia_en_bd_estudiantes(registros: list):
    from app.database.supabase_client import supabase

    errores = []

    carreras = supabase.table("carreras")\
                .select("codigo")\
                .execute()
    
    codigos_carreras = {c["codigo"] for c in carreras.data}

    for i, r in enumerate(registros):
        fila = i+2

        if r["codigo_carrera"] not in codigos_carreras:
            errores.append(f"Fila {fila}: la carrera '{r['codigo_carrera']}' no existe en el sistema")

    return errores

def procesar_archivo_calificaciones(contenido: bytes, nombre_archivo: str):
    df = leer_archivo(contenido, nombre_archivo)
    validar_columnas(df, COLUMNAS_CALIFICACIONES)
    errores = validar_notas(df)

    if errores:
        return None, errores
    
    registros = preparar_registros_calificaciones(df)

    errores_bd = validar_existencia_en_bd_calificaciones(registros)
    if errores_bd:
        return None, errores_bd
    
    return registros, []

def procesar_archivo_secciones(contenido: bytes, nombre_archivo: str):
    df = leer_archivo(contenido, nombre_archivo)
    validar_columnas(df, COLUMNAS_SECCIONES)
    errores = validar_datos_secciones(df)

    if errores:
        return None, errores
    
    registros = preparar_registros_secciones(df)

    errores_bd = validar_existencia_en_bd_secciones(registros)
    if errores_bd:
        return None, errores_bd
    
    return registros, []

def procesar_archivo_estudiantes(contenido: bytes, nombre_archivo: str):
    df = leer_archivo(contenido, nombre_archivo)
    validar_columnas(df, COLUMNAS_ESTUDIANTES)
    errores = validar_datos_estudiantes(df)

    if errores:
        return None, errores
    
    registros = preparar_registros_estudiantes(df)

    errores_bd = validar_existencia_en_bd_estudiantes(registros)
    if errores_bd:
        return None, errores_bd
    
    return registros, []
