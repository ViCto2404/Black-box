from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

print("URL:", url)
print("KEY:", key[:30], "...")

supabase = create_client(url, key)

# Prueba directa sin RLS
resultado = supabase.table("calificacion").select("*").execute()
print("Total registros:", len(resultado.data))

# Si sigue vacío, verifica el schema
resultado2 = supabase.table("calificacion").select("*").limit(1).execute()
print("Prueba limit 1:", resultado2.data)
print("Count:", resultado2.count)