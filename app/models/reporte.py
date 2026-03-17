from pydantic import BaseModel
from typing import Optional

class RendimientoMateria(BaseModel):
    codigo_materia: str
    nombre_materia: str
    codigo_carrera: str
    periodo_academico: str
    total_estudiantes: int
    promedio: float
    porcentaje_aprobacion: float
    procentaje_reprobacion: float

class ResumenPeriodo(BaseModel):
    total_estudiantes_analizados: int
    total_materias: int
    indice_aprobacion_global: float
    cantidad_materias_criticas: int

class MasaEstudiantil(BaseModel):
    codigo_carrera: str
    nombre_carrera: str
    total_activos: int
    total_inactivos: int
    total_general: int
    