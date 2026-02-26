from pydantic import BaseModel, conint, constr
from typing import Optional
from datetime import datetime

ConstrainedStr1000 = constr(max_length=1000)

class FeedbackCreate(BaseModel):
    rating:   Optional[conint(ge=1, le=5)] = None
    thumbs:   Optional[str] = None
    category: Optional[str] = None
    message:  Optional[constr(max_length=1000)] = None  # type: ignore

class FeedbackRead(FeedbackCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True