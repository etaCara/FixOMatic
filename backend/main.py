from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import create_mysql_pool, close_mysql_pool
from routes import tickets, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_mysql_pool()
    yield
    await close_mysql_pool()

app = FastAPI(lifespan=lifespan)

# Route groups
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
