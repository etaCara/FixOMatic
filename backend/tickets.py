from fastapi import APIRouter, HTTPException
import aiomysql
from pydantic import BaseModel
from db import pool

router = APIRouter()

class Ticket(BaseModel):
    id: int | None = None
    title: str
    description: str
    status: str = "open"

@router.get("/tickets")
async def get_all_tickets():
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM tickets")
            result = await cur.fetchall()
            return result

@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
            ticket = await cur.fetchone()
            if not ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")
            return ticket

@router.post("/tickets")
async def create_ticket(ticket: Ticket):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO tickets (title, description, status) VALUES (%s, %s, %s)",
                (ticket.title, ticket.description, ticket.status)
            )
            return {"message": "Ticket created"}

@router.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: int, ticket: Ticket):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE tickets SET title=%s, description=%s, status=%s WHERE id=%s",
                (ticket.title, ticket.description, ticket.status, ticket_id)
            )
            return {"message": "Ticket updated"}

@router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
            return {"message": "Ticket deleted"}
