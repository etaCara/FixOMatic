from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from db import get_connection

router = APIRouter()

# --- Models ---
class TicketCreate(BaseModel):
    title: str
    description: str
    status: str = "open"

class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: str

# --- Routes ---
@router.post("/", response_model=TicketOut)
async def create_ticket(ticket: TicketCreate):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO tickets (title, description, status) VALUES (%s, %s, %s)",
            (ticket.title, ticket.description, ticket.status)
        )
        await conn.commit()
        ticket_id = cur.lastrowid
    return {**ticket.dict(), "id": ticket_id}

@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(ticket_id: int):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, title, description, status FROM tickets WHERE id = %s", (ticket_id,))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket not found")
    return {"id": row[0], "title": row[1], "description": row[2], "status": row[3]}

@router.get("/", response_model=list[TicketOut])
async def list_tickets():
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, title, description, status FROM tickets")
        rows = await cur.fetchall()
    return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3]} for r in rows]
