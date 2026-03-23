from pydantic import BaseModel
from typing import Optional

class EstudianteCreate(BaseModel):
    id_unphu: str
    nombre: str
    codigo_carrera: str
    estado_activo: str = "Activo"
    correo_institucional: Optional[str] = None

class EstudianteUpdate(BaseModel):
    nombre: Optional[str] = None
    estado_activo: Optional[str] = None
    correo_institucional: Optional[str] = None

class EstudianteResponde(BaseModel):
    id_unphu: str
    nombre: str
    codigo_carrera: str
    estado_activo: str
    correo_institucional: Optional[str] = None