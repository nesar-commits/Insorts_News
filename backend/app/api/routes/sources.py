from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.article import get_sources
from app.db.session import get_db
from app.schemas.source import SourceRead

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceRead])
def list_sources(db: Session = Depends(get_db)):
    return get_sources(db)
