from pydantic import BaseModel
from typing import Optional

class DirectorCreate(BaseModel):
    id_unphu: str
    nombre: str
    correo_institucional: str
    codigo_escuela: Optional[str] = None

class DirectorUpdate(BaseModel):
    nombre: Optional[str] = None
    correo_institucional: Optional[str] = None
    codigo_escuela: Optional[str] = None