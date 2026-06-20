from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.core.config import SECRET_KEY


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="TLW",
    description="FastAPI + SQLite + SQLAdmin",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
setup_admin(app)


@app.get("/")
def root():
    return {
        "message": "API работает",
        "admin": "/admin",
        "docs": "/docs",
    }
