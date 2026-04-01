from pydantic import BaseModel, field_validator
from typing import Optional

class CarreraCreate(BaseModel):
    codigo: str
    nombre: str
    codigo_escuela: str
    duracion_anos: int
    estado: str = "Activa"

    @field_validator("duracion_anos")
    def validar_duracion(cls, v):
        if not 1 <= v <= 7:
            raise ValueError("La duración debe estar entre 1 y 7 años")
        return v

class CarreraUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo_escuela: Optional[str] = None
    duracion_anos: Optional[int] = None
    estado: Optional[str] = None