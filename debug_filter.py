
from app.database.supabase_client import supabase

def test_materia_filter():
    # Probar el filtro que está fallando
    escuela = "ISC" # O una escuela que sepas que tiene datos
    print(f"Probando filtro para escuela: {escuela}")
    
    # Intento 1: Como está actualmente
    try:
        res1 = supabase.table("materia").select("codigo").eq("carreras.codigo_escuela", escuela).execute()
        print(f"Intento 1 (select 'codigo'): {len(res1.data)} materias encontradas")
    except Exception as e:
        print(f"Intento 1 falló: {e}")

    # Intento 2: Con join explícito !inner
    try:
        res2 = supabase.table("materia").select("codigo, carreras!inner(codigo_escuela)").eq("carreras.codigo_escuela", escuela).execute()
        print(f"Intento 2 (select con !inner): {len(res2.data)} materias encontradas")
    except Exception as e:
        print(f"Intento 2 falló: {e}")

if __name__ == "__main__":
    test_materia_filter()
