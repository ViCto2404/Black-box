from pydantic import BaseModel, field_validator
from typing import Optional

class MateriaCreate(BaseModel):
    codigo: str
    nombre: str
    codigo_carrera: str
    creditos: int
    id_profesor: Optional[str] = None
    cupo_maximo: int
    estado: str = "Activa"

    @field_validator("creditos")
    def validar_creditos(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("Los créditos deben estar entre 1 y 12")
        return v

    @field_validator("cupo_maximo")
    def validar_cupo(cls, v):
        if v <= 0:
            raise ValueError("El cupo máximo debe ser mayor a 0")
        return v

class MateriaUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo_carrera: Optional[str] = None
    creditos: Optional[int] = None
    id_profesor: Optional[str] = None
    cupo_maximo: Optional[int] = None
    estado: Optional[str] = None