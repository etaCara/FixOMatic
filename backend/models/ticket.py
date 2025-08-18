from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TicketBase(BaseModel):
    title: str
    description: str
    status: Optional[str] = "open"
    assigned_to: Optional[str] = None
    severity: Optional[str] = "Low"


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    severity: Optional[str] = None


class TicketResponse(TicketBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
