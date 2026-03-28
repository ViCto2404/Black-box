from pydantic import BaseModel
from typing import Optional

class SeccionCreate(BaseModel):
    codigo_seccion: str
    materia: str
    profesor: Optional[str] = None
    periodo: str
    aula: Optional[str] = None
    cupo_max: int
    horario: Optional[str] = None
    estado: str = "Activa"

class SeccionUpdate(BaseModel):
    profesor: Optional[str] = None
    aula: Optional[str] = None
    cupo_max: Optional[int] = None
    horario: Optional[str] = None
    estado: Optional[str] = None