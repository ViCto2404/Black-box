from pydantic import baseModel
from typing import Optional

class EstudianteCreate(baseModel):
    id_unphu: str
    nombre: str
    codigo_carrera: str
    estado_activo: str = "Activo"
    correo_institucional: Optional[str] = None

class EstudianteUpdate(baseModel):
    nombre: Optional[str] = None
    estado_activo: Optional[str] = None
    correo_institucional: Optional[str] = None

class EstudianteResponde(baseModel):
    id_unphu: str
    nombre: str
    codigo_carrera: str
    estado_activo: str
    correo_institucional: Optional[str] = None