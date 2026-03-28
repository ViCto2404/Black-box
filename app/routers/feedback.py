from fastapi import APIRouter, HTTPException, Query
from app.services import feedback as svc
from app.models.feedback import FeedbackCreate

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.get("/")
def listar_feedback(
    anonimo: bool = Query(default=None),
    codigo_carrera: str = Query(default=None)
):
    return svc.get_feedback(anonimo, codigo_carrera)

@router.get("/resumen")
def resumen_feedback():
    return svc.get_resumen_feedback()

@router.post("/", status_code=201)
def crear_feedback(payload: FeedbackCreate):
    feedback, error = svc.crear_feedback(payload.model_dump())
    if error:
        raise HTTPException(status_code=400, detail=error)
    return feedback

@router.delete("/{id_feedback}", status_code=204)
def eliminar_feedback(id_feedback: int):
    ok, error = svc.eliminar_feedback(id_feedback)
    if error:
        raise HTTPException(status_code=404, detail=error)