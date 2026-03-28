from pydantic import BaseModel
from typing import Optional

class EscuelaCreate(BaseModel):
    codigo: str
    nombre: str
    id_director: str          # obligatorio
    estado: str = "Activa"

class EscuelaUpdate(BaseModel):
    nombre: Optional[str] = None
    id_director: Optional[str] = None
    estado: Optional[str] = None