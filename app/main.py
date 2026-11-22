from contextlib import asynccontextmanager
from pathlib import Path
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import init_db
from app.routers import auth, courses, sessions, stats

settings = get_settings()

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_PATH = STATIC_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="A complete Study Tracker REST API built with FastAPI, SQLModel, and JWT authentication.",
    lifespan=lifespan,
)

# CORS Middleware (Lesson 8)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Timing Middleware (Lesson 8)
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
    return response


# Mount Static Files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Core / Base routes
@app.get("/", tags=["root"])
def read_root(request: Request):
    accept = request.headers.get("accept", "")
    # If a browser requests HTML, serve the frontend app
    if "text/html" in accept and INDEX_PATH.exists():
        return FileResponse(str(INDEX_PATH))
    # Otherwise return JSON API discovery response
    return {
        "message": "Welcome to the Study Tracker API",
        "docs": "/docs",
        "version": settings.app_version,
    }


@app.get("/app", tags=["frontend"])
def read_frontend_app():
    """Direct route to frontend application"""
    if INDEX_PATH.exists():
        return FileResponse(str(INDEX_PATH))
    return {"message": "Frontend static file not found"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# Include Routers (Lesson 8)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(sessions.router)
app.include_router(stats.router)
