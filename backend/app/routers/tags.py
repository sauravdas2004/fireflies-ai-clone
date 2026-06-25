from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tag
from app.schemas.common import TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)):
    return db.scalars(__import__("sqlalchemy").select(Tag)).all()


@router.post("", response_model=TagRead)
def create_tag(name: str, db: Session = Depends(get_db)):
    normalized = name.strip().lower()
    if not normalized:
        return TagRead.model_validate(Tag(id=0, name=normalized))
    existing = db.scalar(__import__("sqlalchemy").select(Tag).where(Tag.name == normalized))
    if existing:
        return existing
    tag = Tag(name=normalized)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
