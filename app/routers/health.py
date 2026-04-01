from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(tags=["Saúde"])

@router.get("/health")
def health(db: Session = Depends(get_db)):
    """Verifica a saúde da aplicação e do banco de dados. Retorna 'ok' se ambos estiverem operacionais, ou 'error' para o banco se houver falha na conexão."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "database": db_status
    }