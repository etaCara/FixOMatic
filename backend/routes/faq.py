# models/faq.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FAQOut(BaseModel):
    KAID: str
    title: str
    author: str
    content: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# -------- GET ALL FAQS --------
@router.get("/faq", response_model=List[FAQOut])
async def get_all_faqs():
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("""
            SELECT KAID, title, author, content, created_at, updated_at
            FROM knowledge_articles
        """)
        rows = await cur.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No FAQs found")

    return [
        FAQOut(
            KAID=row[0],
            title=row[1],
            author=row[2],
            content=row[3],
            created_at=row[4],
            updated_at=row[5]
        )
        for row in rows
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
        KAID=row[0],
        title=row[1],
        author=row[2],
        content=row[3],
        created_at=row[4],
        updated_at=row[5]
    )
