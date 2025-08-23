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
    created_by: Optional[str] = None  # maps to customerID

class TicketOut(BaseModel):
    id: int  #  TicketID
    title: str
    description: str
    status: str
    created_by: Optional[str] = None
    created_at: Optional[str] = None

class TicketUpdate(BaseModel):
    title: str
    description: str
    status: str
    severity: str | None = None

# --- Routes ---

@router.put("/{ticket_id}")
async def update_ticket(ticket_id: int, ticket: TicketUpdate):
    conn = await get_connection()
    async with conn.cursor() as cur:
        # Check if the ticket exists
        await cur.execute("SELECT TicketID FROM tickets WHERE TicketID=%s", (ticket_id,))
        existing_ticket = await cur.fetchone()
        if not existing_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Update ticket
        await cur.execute("""
            UPDATE tickets
            SET title=%s, description=%s, status=%s, severity=%s, last_updated_datetime=NOW()
            WHERE TicketID=%s
        """, (
            ticket.title,
            ticket.description,
            ticket.status,
            ticket.severity,
            ticket_id
        ))

        await conn.commit()

    return {
        "message": "Ticket updated successfully",
        "ticket_id": ticket_id
    }

@router.post("/", response_model=TicketOut)
async def create_ticket(ticket: TicketCreate):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO tickets (title, description, status, customerID)
            VALUES (%s, %s, %s, %s)
            """,
            (ticket.title, ticket.description, ticket.status, ticket.created_by)
        )
        await conn.commit()
        ticket_id = cur.lastrowid

        await cur.execute(
            """
            SELECT TicketID, title, description, status, customerID, opened_datetime
            FROM tickets
            WHERE TicketID = %s
            """,
            (ticket_id,)
        )
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

@router.get("/in-progress", response_model=List[TicketOut])
async def get_in_progress_tickets():
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT TicketID, title, description, status, created_by, opened_datetime
            FROM tickets
            WHERE status = 'In-Process'
            """
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

@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(ticket_id: str):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT TicketID, title, description, status, customerID, opened_datetime
            FROM tickets
            WHERE TicketID = %s
            """,
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
                """
                SELECT TicketID, title, description, status, customerID, opened_datetime
                FROM tickets
                WHERE customerID = %s
                """,
                (user,)
            )
        else:
            await cur.execute(
                """
                SELECT TicketID, title, description, status, customerID, opened_datetime
                FROM tickets
                """
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
