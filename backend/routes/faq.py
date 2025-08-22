from fastapi import APIRouter
from pydantic import BaseModel
from db import get_connection

router = APIRouter()

class FAQItem(BaseModel):
    question: str
    answer: str

@router.get("/", response_model=list[FAQItem])
async def get_faqs():
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("SELECT question, answer FROM faqs")
        rows = await cur.fetchall()
    return [{"question": r[0], "answer": r[1]} for r in rows]
