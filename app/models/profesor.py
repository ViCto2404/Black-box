from pydantic import BaseModel
from typing import Optional

class ProfesorCreate(BaseModel):
    id_profesor: str
    nombre: str
    correo_institucional: str
    codigo_carrera: Optional[str] = None
    estado: str = "Activo"

class ProfesorUpdate(BaseModel):
    nombre: Optional[str] = None
    correo_institucional: Optional[str] = None
    codigo_carrera: Optional[str] = None
    estado: Optional[str] = None