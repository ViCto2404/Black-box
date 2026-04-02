from fastapi import APIRouter, HTTPException, Header
from app.services.auth import login, logout
from app.models.auth import LoginRequest

router = APIRouter(prefix="/auth", tags=["Autenticación"])


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