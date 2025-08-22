from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import aiomysql
from db import pool

router = APIRouter()

# --- Models ---
class Ticket(BaseModel):
    id: int | None = None
    title: str
    description: str
    status: str = "open"

# --- Routes ---
@router.get("/tickets/", response_model=list[Ticket])
async def get_all_tickets():
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM tickets")
            result = await cur.fetchall()
            return result

@router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
            ticket = await cur.fetchone()
            if not ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")
            return ticket

@router.post("/tickets/", response_model=Ticket)
async def create_ticket(ticket: Ticket):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO tickets (title, description, status) VALUES (%s, %s, %s)",
                (ticket.title, ticket.description, ticket.status)
            )
            ticket_id = cur.lastrowid
            await conn.commit()
    return Ticket(id=ticket_id, **ticket.dict())

@router.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: int, ticket: Ticket):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            affected = await cur.execute(
                "UPDATE tickets SET title=%s, description=%s, status=%s WHERE id=%s",
                (ticket.title, ticket.description, ticket.status, ticket_id)
            )
            await conn.commit()
            if affected == 0:
                raise HTTPException(status_code=404, detail="Ticket not found")
    return Ticket(id=ticket_id, **ticket.dict())

@router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            affected = await cur.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
            await conn.commit()
            if affected == 0:
                raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": f"Ticket #{ticket_id} deleted successfully"}
