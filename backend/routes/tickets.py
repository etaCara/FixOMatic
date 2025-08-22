from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from db import get_connection

router = APIRouter()

# --- Models ---
class TicketCreate(BaseModel):
    title: str
    description: str
    status: str = "open"
    created_by: Optional[str] = None  # Add tracking of creator (optional)

class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_by: Optional[str] = None  # Include creator in response
    created_at: Optional[str] = None  # Assuming ticket has timestamp

# --- Routes ---

@router.post("/", response_model=TicketOut)
async def create_ticket(ticket: TicketCreate):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO tickets (title, description, status, created_by)
            VALUES (%s, %s, %s, %s)
            """,
            (ticket.title, ticket.description, ticket.status, ticket.created_by)
        )
        await conn.commit()
        ticket_id = cur.lastrowid

        # Fetch created ticket to return complete info (created_at, etc.)
        await cur.execute("SELECT id, title, description, status, created_by, created_at FROM tickets WHERE id = %s", (ticket_id,))
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=500, detail="Ticket creation failed")

    return TicketOut(
        id=row[0],
        title=row[1],
        description=row[2],
        status=row[3],
        created_by=row[4],
        created_at=str(row[5]) if row[5] else None
    )

@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(ticket_id: int):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, title, description, status, created_by, created_at FROM tickets WHERE id = %s",
            (ticket_id,)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketOut(
        id=row[0],
        title=row[1],
        description=row[2],
        status=row[3],
        created_by=row[4],
        created_at=str(row[5]) if row[5] else None
    )

@router.get("/", response_model=List[TicketOut])
async def list_tickets(user: Optional[str] = Query(default=None)):
    conn = await get_connection()
    async with conn.cursor() as cur:
        if user:
            await cur.execute(
                "SELECT id, title, description, status, created_by, created_at FROM tickets WHERE created_by = %s",
                (user,)
            )
        else:
            await cur.execute(
                "SELECT id, title, description, status, created_by, created_at FROM tickets"
            )
        rows = await cur.fetchall()

    return [
        TicketOut(
            id=r[0],
            title=r[1],
            description=r[2],
            status=r[3],
            created_by=r[4],
            created_at=str(r[5]) if r[5] else None
        ) for r in rows
    ]
