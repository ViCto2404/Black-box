from pydantic import BaseModel, field_validator
from typing import Optional

class calificacionCreate(BaseModel):
    id_estudiante: str
    codigo_materia: str
    nota: float
    periodo_academico: str

    @field_validator("nota")
    def validar_nota(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("La nota debe estar entre 0 y 100")
        return v
    
class calificacionResponde(BaseModel):
    id: int
    id_estudiante: str
    codigo_materia: str
    nota: float
    periodo_academico: str