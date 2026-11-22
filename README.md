# Study Tracker REST API

A production-ready, authenticated REST API for tracking courses and study sessions, calculating study streaks, and monitoring progress. Built with **FastAPI**, **SQLModel**, **Pydantic v2**, and secured with **Argon2** password hashing and **JWT** bearer tokens.

---

## Architecture Overview

```
                          +------------------------+
                          |   HTTP Client / Web    |
                          +-----------+------------+
                                      |
                     [Bearer JWT / OAuth2 Password Flow]
                                      |
                                      v
                      +--------------------------------+
                      |   FastAPI Application (ASGI)   |
                      |  - CORS & Timing Middleware    |
                      |  - Pydantic v2 Serialization   |
                      +---------------+----------------+
                                      |
            +-------------------------+-------------------------+
            |                         |                         |
     +------v------+           +------v------+           +------v------+
     | /auth       |           | /courses    |           | /sessions   |
     | - /register |           | - CRUD      |           | - Log &     |
     | - /token    |           | - Per-user  |           |   filter    |
     | - /me       |           |   isolation |           | /stats      |
     +------+------+           +------+------+           +------+------+
            |                         |                         |
            +-------------------------+-------------------------+
                                      |
                         [SQLModel / SQLAlchemy ORM]
                                      |
                                      v
                         +--------------------------+
                         |  SQLite / PostgreSQL DB  |
                         +--------------------------+
```

---

## Features

- **Authentication & Security (Lessons 3 & 7)**
  - User registration (`POST /auth/register`) with input validation and unique constraints.
  - Password hashing using **Argon2** via `pwdlib[argon2]`.
  - OAuth2 password flow issuing **JWT access tokens** (`POST /auth/token`).
  - Protected endpoints using the `CurrentUser` dependency (`GET /auth/me`).
- **Course Management (Lessons 4, 5 & 6)**
  - Full CRUD operations (`POST`, `GET`, `PATCH`, `DELETE` at `/courses`).
  - Strict **data ownership isolation**: Users can only view, modify, or delete courses they own.
- **Study Sessions & Filtering (Lessons 2 & 6)**
  - Log sessions (`POST /sessions`) with minutes, date, and notes, validating course ownership.
  - List and filter sessions by `course_id`, `start_date`, and `end_date` with pagination.
- **Progress & Streak Analytics (Lesson 6)**
  - `GET /stats`: Computes total minutes, total sessions, breakdown per course, and consecutive **weekly study streak**.
- **Quality & Reliability (Lessons 8 & 9)**
  - Modular project structure using `APIRouter`.
  - Type-safe configuration via `pydantic-settings` (`.env` support).
  - Timing header (`X-Process-Time`) middleware.
  - Automated test suite with **22 passing tests** utilizing an isolated in-memory SQLite database (`StaticPool`).
- **Deployment (Lesson 10)**
  - Containerized with multi-stage layer cached `Dockerfile`.

---

## Project Structure

```
Study-Tracker/
|-- app/
|   |-- __init__.py
|   |-- config.py         # Settings with pydantic-settings
|   |-- database.py       # Engine and session dependency
|   |-- models.py         # SQLModel database tables and Pydantic schemas
|   |-- security.py       # Argon2 hashing & JWT helpers
|   |-- main.py           # App creation, middleware, router inclusions
|   |-- routers/
|   |   |-- auth.py       # Register, login, me
|   |   |-- courses.py    # Courses CRUD
|   |   |-- sessions.py   # Sessions CRUD & filters
|   |   |-- stats.py      # Aggregations & weekly streak
|   `-- tests/
|       |-- conftest.py   # Test fixtures & in-memory database
|       |-- test_auth.py
|       |-- test_courses.py
|       |-- test_health.py
|       |-- test_sessions.py
|       `-- test_stats.py
|-- Dockerfile            # Container deployment image
|-- .dockerignore
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Setup Virtual Environment

```bash
# Clone the repository
git clone <repo-url>
cd Study-Tracker

# Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 4. Run the Development Server

```bash
fastapi dev app/main.py
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Running Automated Tests

Run the test suite with `pytest`:

```bash
pytest app/tests -v
```

All 22 tests run against an isolated in-memory SQLite database using `StaticPool` without altering persistent data.

---

## Example Usage with cURL

### 1. Register a user
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "satya", "email": "satya@example.com", "password": "securepassword123"}'
```

### 2. Login to receive JWT access token
```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -F "username=satya" \
  -F "password=securepassword123"
```
*Response:*
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### 3. Create a course
```bash
curl -X POST http://127.0.0.1:8000/courses/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "FastAPI Mastery", "description": "From zero to deployed API"}'
```

### 4. Log a study session
```bash
curl -X POST http://127.0.0.1:8000/sessions/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"course_id": 1, "minutes": 45, "notes": "Completed Lesson 7 on JWT auth"}'
```

### 5. View stats & weekly streak
```bash
curl -X GET http://127.0.0.1:8000/stats/ \
  -H "Authorization: Bearer <TOKEN>"
```
*Response:*
```json
{
  "total_minutes": 45,
  "total_sessions": 1,
  "weekly_streak": 1,
  "courses": [
    {
      "course_id": 1,
      "course_title": "FastAPI Mastery",
      "total_minutes": 45,
      "session_count": 1
    }
  ]
}
```

---

## Docker Deployment

### Build the container image:
```bash
docker build -t study-tracker-api .
```

### Run the container:
```bash
docker run -d -p 8000:8000 -e SECRET_KEY="my-production-secret" --name study-tracker study-tracker-api
```
Check health:
```bash
curl http://localhost:8000/health
```
