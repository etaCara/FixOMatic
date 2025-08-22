from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_connection

router = APIRouter()

class UserOut(BaseModel):
    username: str
    role: str

@router.get("/{username}", response_model=UserOut)
async def get_user(username: str):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute("SELECT username, role FROM users WHERE username = %s", (username,))
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
    return {"username": row[0], "role": row[1]}
