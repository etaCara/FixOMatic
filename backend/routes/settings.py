from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_connection

router = APIRouter()

class SettingsUpdate(BaseModel):
    username: str
    dark_mode: bool = False
    notifications: bool = True

@router.put("/")
async def update_settings(settings: SettingsUpdate):
    conn = await get_connection()
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO user_settings (username, dark_mode, notifications)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
              dark_mode = VALUES(dark_mode),
              notifications = VALUES(notifications)
            """,
            (settings.username, settings.dark_mode, settings.notifications)
        )
        await conn.commit()
    return {"message": "Settings updated"}
