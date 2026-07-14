from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from exceptions import AppException
from routers import auth, tasks

import models  # noqa: F401  (registers User/Task with Base before create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once on startup, before the app starts accepting requests
    print("Starting up... creating tables if they don't exist yet.")
    Base.metadata.create_all(bind=engine)
    yield
    # runs once on shutdown
    print("Shutting down.")


app = FastAPI(title="Task Management API", lifespan=lifespan)


# ---------- CORS ----------
# only allow requests from the local frontend dev server, not from
# any random website - this matters once you have a real frontend
# running on localhost:3000 trying to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- request logging middleware ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    print(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


# ---------- global exception handlers ----------
# both handlers below produce the exact same JSON shape, so API
# consumers only ever have to deal with one error format, no matter
# whether it came from a built-in HTTPException or our own AppException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail, "status": exc.status_code},
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail, "status": exc.status_code},
    )


# ---------- routers ----------
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


@app.get("/")
def read_root():
    return {"message": "Task Management API is running. See /docs for the interactive API."}
