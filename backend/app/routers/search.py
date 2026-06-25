from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search import GlobalSearchResponse
from app.services.meetings import search_workspace

router = APIRouter(tags=["search"])


@router.get("/search", response_model=GlobalSearchResponse)
def search(q: str = Query(min_length=1), db: Session = Depends(get_db)):
    return {"query": q, "results": search_workspace(db, q)}
