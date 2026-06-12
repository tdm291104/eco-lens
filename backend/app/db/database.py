"""
SQLite database setup (SQLAlchemy).

- Tạo engine SQLite (file eco_lens.db ở thư mục backend/)
- init_db(): tạo file database + toàn bộ table nếu chưa tồn tại
  (gọi khi app khởi động, và lazy gọi lại trong get_session() để các
  skill có thể dùng DB ngay cả khi gọi ngoài vòng đời FastAPI - ví dụ test)
- get_session(): trả về một SQLAlchemy session mới để skill/API truy vấn
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent.parent / "eco_lens.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class cho mọi ORM model."""


def init_db() -> None:
    """Tạo file SQLite + toàn bộ table nếu chưa tồn tại."""
    from app.db import models  # noqa: F401 - đăng ký model với Base.metadata

    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Trả về một SQLAlchemy session mới (đảm bảo DB/table đã được tạo)."""
    init_db()
    return SessionLocal()
