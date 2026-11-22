from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers import auth, courses, sessions, stats

settings = get_settings()


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


# Core / Base routes
@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "Welcome to the Study Tracker API",
        "docs": "/docs",
        "version": settings.app_version,
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# Include Routers (Lesson 8)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(sessions.router)
app.include_router(stats.router)
