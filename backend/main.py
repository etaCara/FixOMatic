from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db import init_db_pool, close_db_pool
from routes import auth, tickets, user, admin, faq, settings

# --- Lifespan for DB Connection Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    yield
    await close_db_pool()

app = FastAPI(lifespan=lifespan)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(faq.router, prefix="/knowledge", tags=["FAQ"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])

# --- Optional Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Fix-O-Matic backend is running"}
