import pandas as pd
from io import BytesIO

COLUMNAS_REQUERIDAS = {"id_estudiante", "codigo_materia", "nota", "periodo_academico"}

def leer_archivo(contenido: bytes, nombre_archivo: str) -> pd.DataFrame:
    if nombre_archivo.endswith(".csv"):
        df = pd.read_csv(BytesIO(contenido))
    elif nombre_archivo.endswith((".xlsx", ".xls")):
        df.read_excel(BytesIO(contenido))
    else: 
        raise ValueError("Formato no soportado. Use CSV o Excel")
    return df

def validar_columnas(df: pd.DataFrame):
    columnas_archivo = set(df.columns.str.strip().str.lower())
    faltantes = COLUMNAS_REQUERIDAS - columnas_archivo
    if faltantes:
        raise ValueError(f"Columnas faltantes en el archivo: {faltantes}")

def validar_notas(df: pd.DataFrame):
    errores = []

    for i, row in df.iterrows():
        fila = i+2

        if pd.isna(row["nota"]):
            errores.append(f"Fila {fila}: nota vacía")
            continue

        try:
            nota = float(row["nota"])
        except ValueError:
            errores.append(f"Fila {fila}: nota '{row["nota"]}' no es un numero")
            continue

        if not 0 <= nota <= 100:
            errores.append(f"Fila {fila}: nota {nota} fuera del rango 0-100")

        if pd.isna(row["id_estudiante"]) or str(row["id_estudiante"]).strip() == "":
            errores.append(f"Fila {fila}: id_estudiante vacio")

        if pd.isna(row["codigo_materia"]) or str(row["codigo_materia"]).strip() == "":
            errores.append(f"Fila {fila}: codigo_materia vacio")

        if pd.isna(row["periodo_academico"]) or str(row["periodo_academico"]).strip() == "":
            errores.append(f"Fila {fila}: periodo_academico vacio")
        
    return errores

def preparar_registros(df: pd.DataFrame) -> list:
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=["id_estudiante", "codigo_materia", "nota", "periodo_academico"])

    registros = []
    for _, row in df.iterrows():
        registros.append({
            "id_estudiante": str(row["id_estudiante"]).strip(),
            "codigo_materia": str(row["codigo_materia"]).strip(),
            "nota": round(float(row["nota"]), 2),
            "periodo_academico": str(row["periodo_academico"]).strip()
        })

    return registros

def validar_existencia_en_bd(registros: list):
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
            errores.append(f"Fila {fila}: el estudiante '{r["id_estudiante"]}' no existe en el sistema")

        if r["codigo_materia"] not in codigos_materias:
            errores.append(f"Fila {fila}: la materia '{r["codigo_materia"]}' no existe en el sistema")

    return errores

def procesar_archivo(contenido: bytes, nombre_archivo: str):
    df = leer_archivo(contenido, nombre_archivo)
    validar_columnas(df)
    errores = validar_notas(df)

    if errores:
        return None, errores
    
    registros = preparar_registros(df)

    errores_bd = validar_existencia_en_bd(registros)
    if errores_bd:
        return None, errores_bd
    
    return registros, []