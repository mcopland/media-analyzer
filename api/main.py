import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.filters import router as filters_router
from api.routers.media import router as media_router


def create_app(db: sqlite3.Connection) -> FastAPI:
    app = FastAPI(title="Media Analyzer")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.state.db = db
    app.include_router(media_router, prefix="/api")
    app.include_router(filters_router, prefix="/api")

    return app


def _build_prod_app() -> FastAPI:
    from scanner.config import load_config
    from scanner.db import init_db

    cfg = load_config("config.toml")
    conn = sqlite3.connect(cfg.scanner.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return create_app(conn)


try:
    app = _build_prod_app()
except (FileNotFoundError, KeyError, Exception):
    app = None  # type: ignore[assignment]
