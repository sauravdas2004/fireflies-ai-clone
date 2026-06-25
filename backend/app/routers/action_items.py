from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.action_items import ActionItemCreate, ActionItemRead, ActionItemUpdate
from app.services.meetings import add_action_item, delete_action_item, update_action_item

router = APIRouter(tags=["action-items"])


@router.post("/meetings/{meeting_id}/action-items", response_model=ActionItemRead)
def create_action_item(meeting_id: int, payload: ActionItemCreate, db: Session = Depends(get_db)):
    return add_action_item(db, meeting_id, payload)


@router.put("/action-items/{action_item_id}", response_model=ActionItemRead)
def edit_action_item(action_item_id: int, payload: ActionItemUpdate, db: Session = Depends(get_db)):
    return update_action_item(db, action_item_id, payload)


@router.delete("/action-items/{action_item_id}")
def remove_action_item(action_item_id: int, db: Session = Depends(get_db)):
    delete_action_item(db, action_item_id)
    return {"message": "Action item deleted"}
