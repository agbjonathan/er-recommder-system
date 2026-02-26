from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackRead

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("", response_model=FeedbackRead, status_code=201)
def submit_feedback(payload: FeedbackCreate, request: Request, db: Session = Depends(get_db)):
    entry = Feedback(
        **payload.model_dump(),
        user_agent=request.headers.get("user-agent")
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("", response_model=list[FeedbackRead])
def get_feedback(db: Session = Depends(get_db)):
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()