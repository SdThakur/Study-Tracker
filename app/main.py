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


@app.get("/db", tags=["database"])
def view_database_browser():
    """Interactive visual database viewer in browser"""
    import sqlite3
    from fastapi.responses import HTMLResponse

    db_path = Path("study_tracker.db")
    if not db_path.exists():
        return HTMLResponse("<html><body style='font-family:sans-serif;padding:2rem'><h2>Database file not found yet. Run the app to create tables.</h2></body></html>")

    conn = sqlite3.connect("study_tracker.db")
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]

    html_parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Database Viewer - Study Tracker</title>",
        "<script src='https://cdn.tailwindcss.com'></script>",
        "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap' rel='stylesheet'>",
        "<style>body { font-family: 'Inter', sans-serif; background: #fbfbfb; } .font-mono { font-family: 'JetBrains Mono', monospace; }</style>",
        "</head><body class='p-6 max-w-6xl mx-auto text-zinc-900'>",
        "<div class='flex items-center justify-between pb-6 border-b border-zinc-200 mb-6'>",
        "<div><h1 class='text-xl font-bold tracking-tight'>SQLite Database Explorer</h1>",
        "<p class='text-xs text-zinc-500 mt-1 font-mono'>study_tracker.db &middot; " + str(len(tables)) + " tables</p></div>",
        "<div class='flex space-x-2'>",
        "<a href='/db' class='px-3 py-1.5 text-xs font-medium bg-zinc-900 text-white rounded-lg hover:bg-zinc-800'>Refresh</a>",
        "<a href='/app' class='px-3 py-1.5 text-xs font-medium bg-zinc-100 text-zinc-700 rounded-lg hover:bg-zinc-200'>Open App &rarr;</a>",
        "</div></div>",
    ]

    for table in tables:
        cur.execute(f"PRAGMA table_info('{table}')")
        columns = [col[1] for col in cur.fetchall()]
        cur.execute(f"SELECT * FROM '{table}'")
        rows = cur.fetchall()

        html_parts.append(f"<div class='mb-8 bg-white border border-zinc-200 rounded-xl overflow-hidden shadow-sm'>")
        html_parts.append(f"<div class='px-5 py-3.5 bg-zinc-50 border-b border-zinc-200 flex items-center justify-between'>")
        html_parts.append(f"<span class='text-xs font-bold uppercase tracking-wider text-zinc-800 font-mono'>{table}</span>")
        html_parts.append(f"<span class='text-xs text-zinc-500 font-mono'>{len(rows)} rows</span></div>")

        if not rows:
            html_parts.append("<div class='p-6 text-center text-xs text-zinc-400'>Table is currently empty.</div>")
        else:
            html_parts.append("<div class='overflow-x-auto'><table class='w-full text-left text-xs'>")
            html_parts.append("<thead class='bg-zinc-100/70 border-b border-zinc-200 text-zinc-600 font-medium'><tr>")
            for col in columns:
                html_parts.append(f"<th class='py-2.5 px-4 font-mono'>{col}</th>")
            html_parts.append("</tr></thead><tbody class='divide-y divide-zinc-100 text-zinc-700'>")
            for row in rows:
                html_parts.append("<tr class='hover:bg-zinc-50/80'>")
                for val in row:
                    val_str = str(val) if val is not None else "<span class='text-zinc-300'>NULL</span>"
                    if len(val_str) > 30 and "$argon2" in val_str:
                        val_str = "<span class='font-mono text-zinc-400'>[argon2_hash]</span>"
                    html_parts.append(f"<td class='py-2.5 px-4 font-mono truncate max-w-xs'>{val_str}</td>")
                html_parts.append("</tr>")
            html_parts.append("</tbody></table></div>")
        html_parts.append("</div>")

    conn.close()
    html_parts.append("</body></html>")
    return HTMLResponse("".join(html_parts))


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# Include Routers (Lesson 8)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(sessions.router)
app.include_router(stats.router)
