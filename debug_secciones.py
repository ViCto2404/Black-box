from app.database.supabase_client import supabase
import pandas as pd

def debug_secciones(codigo_materia, periodo):
    print(f"Buscando calificaciones para {codigo_materia} en {periodo}...")
    res = supabase.table("calificacion") \
        .select("nota, id_seccion, id_estudiante, codigo_materia") \
        .eq("codigo_materia", codigo_materia) \
        .eq("periodo_academico", periodo) \
        .execute()
    
    if not res.data:
        print("No hay datos.")
        return

    df = pd.DataFrame(res.data)
    print("\nCalificaciones encontradas:")
    print(df.head())
    
    print("\nConteo por id_seccion:")
    print(df.groupby("id_seccion").size())
    
    print("\nValores únicos de id_seccion:")
    print(df["id_seccion"].unique())

    # También ver qué hay en la tabla seccion
    res_s = supabase.table("seccion").select("*").eq("materia", codigo_materia).eq("periodo", periodo).execute()
    print("\nSecciones en tabla 'seccion':")
    for s in res_s.data:
        print(s)

if __name__ == "__main__":
    # Prueba con una materia que sepas que tiene varias secciones
    # Si no sabes una, el usuario dice que "hay materias que tienen mas de una"
    # Vamos a buscar una materia que tenga más de una sección en 'seccion'
    res_m = supabase.rpc("get_materias_con_multiples_secciones", {}).execute() # rpc no existe probablemente
    
    # Intento simple:
    debug_secciones("ISC-401", "1-2024") # Cambia por una real si falla
