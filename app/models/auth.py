from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    id_unphu: str
    nombre: str
    codigo_escuela: str | None = None
    codigo_carrera: str | None = None
    estado: str = "Activo"

class AdminCreate(BaseModel):
    id_unphu: str
    email: str
    password: str
    nombre: str