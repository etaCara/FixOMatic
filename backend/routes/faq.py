from typing import List 
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from db import get_connection

router = APIRouter()  

class FAQOut(BaseModel):
    id: str
    title: str
    author: str
    content: str
    created_at: Optional[str]


# -------- GET ALL FAQS --------
@router.get("/faq", response_model=List[FAQOut])
async def get_all_faq():
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT KAID, title, author, description, created_datetime
            FROM knowledge_articles
            WHERE retired_datetime IS NULL
            ORDER BY created_datetime DESC
        """)
        rows = await cur.fetchall()

    return [
        FAQOut(
            id=r[0],
            title=r[1],
            author=r[2],
            content=r[3],  
            created_at=str(r[4]) if r[4] else None
        )
        for r in rows
    ]

# -------- GET SINGLE FAQ --------
@router.get("/faq/{ka_id}", response_model=FAQOut)
async def get_faq(ka_id: str):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT KAID, title, author, content, created_at, updated_at
            FROM knowledge_articles
            WHERE KAID = %s
        """, (ka_id,))
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="FAQ not found")

    return FAQOut(
            id=r[0],
            title=r[1],
            author=r[2],
            content=r[3], 
            created_at=str(r[4]) if r[4] else None
    )
