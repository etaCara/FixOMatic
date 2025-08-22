from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_connection

router = APIRouter()

class TicketUpdate(BaseModel):
    status: str
    assigned_to: str | None = None

@router.put("/ticket/{ticket_id}")
async def update_ticket(ticket_id: int, update: TicketUpdate):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            "UPDATE tickets SET status = %s, assigned_to = %s WHERE id = %s",
            (update.status, update.assigned_to, ticket_id)
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        await conn.commit()
    return {"message": "Ticket updated successfully"}
