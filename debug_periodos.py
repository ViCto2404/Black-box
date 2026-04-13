from app.database.supabase_client import supabase

def test_periodos():
    try:
        print("Intentando consultar tabla calificacion...")
        query = supabase.table("calificacion").select("periodo_academico").execute()
        print(f"Respuesta cruda: {query}")
        
        if not query.data:
            print("No hay data en query.data")
            return
            
        periodos = sorted(list(set(item["periodo_academico"] for item in query.data)), reverse=True)
        print(f"Periodos procesados: {periodos}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_periodos()
