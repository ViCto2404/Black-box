from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    id_estudiante: Optional[str] = None
    aspectos_evaluar: Optional[str] = None
    comentario: str
    es_anonimo: bool = True

    @field_validator("comentario")
    def validar_comentario(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("El comentario no puede estar vacio")
        if len(v) > 300:
            raise ValueError("El comentario no puede superar 300 caracteres")
        return v
    
class FeedbackResponse(BaseModel):
    id_feedback: int
    estudiante: Optional[str] = None
    codigo_carrera: Optional[str] = None
    aspectos_evaluar: Optional[str] = None
    comentario: str
    es_anonimo: bool
    fecha_envio: datetime

