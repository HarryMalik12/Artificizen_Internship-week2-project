# Task Management REST API

End-of-week capstone project pulling together everything from the week: FastAPI routing, Pydantic schemas, SQLAlchemy + SQLite, JWT authentication, routers, CORS, a global error handler, and pytest tests.

## Features

- User registration and login with hashed passwords (passlib/bcrypt) and JWT auth (python-jose)
- Task model: title, description, status (pending / in_progress / done), due_date, owner_id (FK to User)
- Full CRUD on tasks: create, read (single + list, filterable by status), update, delete
- Ownership enforcement: every task route filters by `owner_id == current_user.id` server-side, so a user can never see or modify someone else's tasks (verified by a test)
- CORS enabled for `http://localhost:3000`
- A global JSON error handler so every error - whether a built-in `HTTPException` or a custom exception - comes back in the same shape: `{"error": true, "detail": "...", "status": 404}`
- Startup/shutdown lifespan event that creates the database tables automatically
- 7 pytest tests covering register, login, create task, fetch tasks, unauthorized access, duplicate username, and cross-user task isolation

## Project Structure

```
main.py               # app assembly: CORS, middleware, exception handlers, routers
config.py              # loads SECRET_KEY / ALGORITHM from .env
database.py            # engine, SessionLocal, Base, get_db
models.py               # User and Task SQLAlchemy models
schemas.py              # Pydantic request/response schemas
security.py             # password hashing + JWT helpers
exceptions.py           # custom exception classes
dependencies.py         # get_current_user dependency
routers/
    auth.py             # POST /auth/register, POST /auth/token
    tasks.py            # full task CRUD, ownership enforced
tests/
    conftest.py         # in-memory test database fixtures
    test_main.py         # the 7 pytest tests
```

## Setup

```
pip install fastapi "uvicorn[standard]" sqlalchemy "passlib[bcrypt]" "python-jose[cryptography]" python-dotenv python-multipart pytest httpx
cp .env.example .env
```

Edit `.env` and set a real `SECRET_KEY` (see the comment inside `.env.example` for how to generate one).

## Running the API

```
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive Swagger UI - every route should be visible and testable from there.

## Running the tests

```
pytest -v
```

Tests run against a separate in-memory SQLite database (see `tests/conftest.py`), so they never touch your real `task_api.db`.

## Typical flow to try in /docs

1. `POST /auth/register` with `{"username": "...", "email": "...", "password": "..."}`
2. `POST /auth/token` with the same username/password (as form data, not JSON) to get an `access_token`
3. Click "Authorize" in Swagger UI and paste the token
4. `POST /tasks` to create a task
5. `GET /tasks` to list your tasks, optionally with `?status_filter=pending`
6. `PUT /tasks/{id}` to update, `DELETE /tasks/{id}` to remove
