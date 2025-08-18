from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from db import get_connection

router = APIRouter()

# --- Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    username: str | None = None
    role: str | None = None

# --- Routes ---
@router.post("/", response_model=LoginResponse)
async def login(data: LoginRequest):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT username, role FROM users WHERE username = %s AND password = %s",
            (data.username, data.password)
        )
        row = await cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid username or password")

    return LoginResponse(success=True, username=row[0], role=row[1])
