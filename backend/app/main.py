"""
FastAPI application entrypoint.

- Khởi tạo FastAPI app
- Khi startup: init_db() (tạo file SQLite + table nếu chưa có) và
  build_registry() (đăng ký toàn bộ skill của 5 agent vào SkillRegistry,
  lưu ở app.state.registry để các endpoint dùng chung)
- Mount các API router: /api/scan, /api/chat, /api/user/{user_id}/impact,
  /api/disposal-points
- Cấu hình CORS để frontend (React) gọi được API
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents import build_registry
from app.api import chat, disposal_points, scan, user
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.registry = build_registry()
    yield


app = FastAPI(title="EcoLens API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router)
app.include_router(chat.router)
app.include_router(user.router)
app.include_router(disposal_points.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
