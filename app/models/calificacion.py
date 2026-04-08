from pydantic import BaseModel, field_validator
from typing import Optional

class CalificacionCreate(BaseModel):
    id_estudiante:    str
    codigo_materia:   str
    id_seccion:       int
    nota:             float
    periodo_academico: str

    @field_validator("nota")
    def validar_nota(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("La nota debe estar entre 0 y 100")
        return v

class CalificacionResponse(BaseModel):
    id:               int
    id_estudiante:    str
    codigo_materia:   str
    id_seccion:       int
    nota:             float
    periodo_academico: str