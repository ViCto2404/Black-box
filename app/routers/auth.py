from fastapi import APIRouter, HTTPException, Header
from app.services.auth import login, logout, cambiar_contrasena, crear_administrador
from app.models.auth import LoginRequest, AdminCreate
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class CambioPasswordRequest(BaseModel):
    email: str
    password_actual: str
    password_nuevo: str
    password_nuevo_confirmacion: str


@router.post("/login")
def iniciar_sesion(payload: LoginRequest):
    resultado, error = login(payload.email, payload.password)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return resultado


@router.post("/logout")
def cerrar_sesion(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    ok, error = logout(token)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"mensaje": "Sesión cerrada correctamente"}


@router.post("/cambiar-password")
def cambiar_password(payload: CambioPasswordRequest):
    resultado, error = cambiar_contrasena(
        payload.email,
        payload.password_actual,
        payload.password_nuevo,
        payload.password_nuevo_confirmacion
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return resultado

@router.post("/crear-administrador", status_code=201)
def crear_admin(payload: AdminCreate):
    resultado, error = crear_administrador(
        payload.id_unphu,
        payload.email,
        payload.password,
        payload.nombre
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return resultado

