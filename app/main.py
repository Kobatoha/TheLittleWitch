from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.game.router import router as garden_router
from app.game.inventory_router import router as inventory_router
from app.game.shop_router import router as shop_router
from app.game.brew_router import router as brew_router
from app.core.config import SECRET_KEY
from app.core.exceptions import GameError


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="TLW",
    description="FastAPI + SQLite + SQLAdmin",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
setup_admin(app)
app.include_router(garden_router, prefix="/api/game", tags=["garden"])
app.include_router(inventory_router, prefix="/api/game", tags=["inventory"])
app.include_router(shop_router, prefix="/api/game", tags=["shop"])
app.include_router(brew_router, prefix="/api/game", tags=["brew"])


@app.get("/")
def root():
    return {
        "message": "API работает",
        "admin": "/admin",
        "docs": "/docs",
    }

@app.exception_handler(GameError)
async def game_error_handler(request, exc: GameError):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "detail": exc.message,
            "code": exc.code.value,
            "details": exc.details,
        }
    )
